from rest_framework.response import Response
from rest_framework.decorators import api_view
from empenos.models import Tipo_Producto,Linea,Sub_Linea,Marca,Costo_Kilataje,Empenos_Temporal,Joyeria_Empenos_Temporal,Cliente,Boleta_Empeno
from empenos.models import Pagos,Det_Boleto_Empeno,Periodo_Temp
from django.contrib.auth.models import User
from empenos.funciones import fn_calcula_refrendo
import math
from empenos.funciones import *
from django.core import serializers
from empenos.jobs import *
from django.conf import settings

@api_view(['GET'])
def api_tipo_producto(request):
	respuesta=[]
	try:
		lista=[]
		tp=Tipo_Producto.objects.all()
		respuesta.append({'estatus':"1"})
		for x in tp:
			lista.append({'id_tipo_producto':x.id,'tipo_producto':x.tipo_producto})
		respuesta.append({'lista':lista})
	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({'estatus':"0",'msj':"Error al consultar el catalogo de tipo de productos"})#estatus de falla
	return Response(respuesta)



@api_view(['GET'])
def api_notificacion_cajas_abiertas(request):

	hoy = date.today()
	fecha_inicial_hoy = datetime.combine(hoy, time.min) 
	fecha_final_hoy = datetime.combine(hoy, time.max)  

	cajas=Cajas.objects.filter(fecha__range=(fecha_inicial_hoy,fecha_final_hoy),fecha_cierre__isnull=True)

	str_html="<h3>Las siguientes cajas no fueron cerradas:</h3><br>"


	for c in cajas:
		str_html=str_html+"Caja "+c.caja+" del usuario <strong>"+c.usuario.username +"</strong> de la sucursal "+c.sucursal.sucursal+"<br>"

	if cajas.exists():
		fn_envia_mail(str_html,"Notificacion Cajas Abiertas",settings.EMAIL_NOTIFICACIONES)
		fn_envia_mail(str_html,"Notificacion Cajas Abiertas","jasso.gallegos@gmail.com")
	respuesta=[]
	return Response(respuesta)	




@api_view(['GET'])
def api_job_diario(request):
	respuesta=[]
	try:
		fn_job_diario()
		fn_envia_mail("JOB Fechas vencimiento se ejecuto correctamente","Job Vencimientos","jasso.gallegos@gmail.com")
	except Exception as e:
		fn_envia_mail(str(e),"Fallo Job Vencimientos","jasso.gallegos@gmail.com")
		
	return Response(respuesta)


@api_view(['GET'])
def api_consulta_linea(request):
	id_tipo_producto=request.GET.get("id_tipo_producto")	
	respuesta=[]
	try:		
		tipo_producto=Tipo_Producto.objects.get(id=id_tipo_producto)				
		lista=[]
		respuesta.append({'estatus':"1"})
		lin=Linea.objects.filter(tipo_producto=tipo_producto)
		for x in lin:
			lista.append({'id_linea':x.id,'linea':x.linea})
		respuesta.append({'lista':lista})
	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error a consultar el catalogo de lineas"})

	return Response(respuesta)

@api_view(['GET'])
def api_consulta_sublinea(request):
	id_linea=request.GET.get("id_linea")

	respuesta=[]

	try:
		linea=Linea.objects.get(id=id_linea)
		lista=[]
		respuesta.append({"estatus":"1"})
		subl=Sub_Linea.objects.filter(linea=linea)
		for x in subl:
			lista.append({"id_sublinea":x.id,"sublinea":x.sub_linea})
		respuesta.append({"lista":lista})

	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error a consultar el catalogo de sublineas"})
	return Response(respuesta)

@api_view(['GET'])
def api_consulta_marcas(request):
	respuesta=[]

	try:		
		lista=[]
		respuesta.append({"estatus":"1"})
		subl=Marca.objects.all()
		for x in subl:
			lista.append({"id_marca":x.id,"marca":x.marca})
		respuesta.append({"lista":lista})

	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error a consultar el catalogo de marcas."})
	return Response(respuesta)

@api_view(["GET"])
def api_consulta_kilataje(request):
	id_tipo_producto=request.GET.get("id_tipo_producto")
	respuesta=[]
	try:
		id_tipo_producto=Tipo_Producto.objects.get(id=id_tipo_producto)
		lista=[]
		respuesta.append({"estatus":"1"})
		ck=Costo_Kilataje.objects.filter(tipo_producto=id_tipo_producto)
		for x in ck:
			lista.append({'id_kilataje':x.id,"kilataje":x.kilataje})
		respuesta.append({"lista":lista})
	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al consultar el catalogo de kilatajes."})

	return Response(respuesta)

@api_view(['GET'])
def api_consulta_costo_kilataje(request):
	id_kilataje=request.GET.get("id_kilataje")
	respuesta=[]
	try:
		k=Costo_Kilataje.objects.get(id=id_kilataje)
		respuesta.append({"estatus":"1"})
		respuesta.append({"costo":k.avaluo})
	except Exception as e:
		print (e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al consultar el kilataje"})
	return Response(respuesta)


@api_view(['GET'])
def api_guarda_producto_temporal(request):
	respuesta=[]
	id_usuario=request.GET.get("id_usuario")
	id_tipo_producto=request.GET.get("id_tipo_producto")
	id_linea=request.GET.get("id_linea")
	id_sublinea=request.GET.get("id_sublinea")
	id_marca=request.GET.get("id_marca")
	descripcion=request.GET.get("descripcion")
	id_kilataje=request.GET.get("id_kilataje")
	peso=request.GET.get("peso")
	avaluo=request.GET.get("avaluo")
	mutuo_sugerido=request.GET.get("mutuo_sugerido")
	mutuo=request.GET.get("mutuo")
	observaciones=request.GET.get("observaciones")
	error="0"
	try:
		respuesta.append({"estatus":"1"})

		usuario=User.objects.get(id=id_usuario)
		tipo_producto=Tipo_Producto.objects.get(id=id_tipo_producto)
		linea=Linea.objects.get(id=id_linea)
		sub_linea=Sub_Linea.objects.get(id=id_sublinea)
		marca=Marca.objects.get(id=id_marca)		
		cotizacion=Empenos_Temporal(usuario=usuario,tipo_producto=tipo_producto,linea=linea,sub_linea=sub_linea,marca=marca,descripcion=descripcion,avaluo=avaluo,mutuo_sugerido=mutuo_sugerido,mutuo=mutuo,observaciones=observaciones)
		cotizacion.save()
		#si es oro o plata cargamos el kilataje
		if id_tipo_producto=="1" or id_tipo_producto=="2":
			costo_kilataje=Costo_Kilataje.objects.get(id=id_kilataje)
			Joyeria_Empenos_Temporal.objects.create(empeno_temporal=cotizacion,peso=peso,costo_kilataje=costo_kilataje)

	except Exception as e:
		print(e)
		error="1"
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al guardar la cotizacion."})


	if error=="1":
		try:
			cotizacion.delete()
		except:
			print("No pasa nada")
	return Response(respuesta)

@api_view(['GET'])
def api_consulta_cotizacion(request):
	respuesta=[]
	id_usuario=request.GET.get("id_usuario")

	try:
		avaluo_oro=0
		avaluo_plata=0
		avaluo_varios=0
		mutuo_oro=0
		mutuo_plata=0
		mutuo_varios=0
		respuesta.append({"estatus":"1"})
		usuario=User.objects.get(id=id_usuario)
		cotizacion=Empenos_Temporal.objects.filter(usuario=usuario)
		lista=[]
		cont_movs=0
		for c in cotizacion:
			cont_movs=cont_movs+1
			if c.tipo_producto.id==1:
				avaluo_oro=avaluo_oro+c.avaluo
				mutuo_oro=mutuo_oro+c.mutuo
			elif c.tipo_producto.id==2:
				avaluo_plata=avaluo_plata+c.avaluo
				mutuo_plata=mutuo_plata+c.mutuo
			elif c.tipo_producto.id==3:
				avaluo_varios=avaluo_varios+c.avaluo
				mutuo_varios=mutuo_varios+c.mutuo
			kilataje=""
			peso=""
			if c.tipo_producto.id==1 or c.tipo_producto.id==2:
				j=Joyeria_Empenos_Temporal.objects.get(empeno_temporal=c)
				print(j)
				kilataje=j.costo_kilataje.kilataje
				peso=j.peso

			lista.append({"id":c.id,"tipo_producto":c.tipo_producto.tipo_producto,"linea":c.linea.linea, "sub_linea":c.sub_linea.sub_linea, "marca":c.marca.marca, "descripcion":c.descripcion, "Kilataje":kilataje, "peso":peso, "avaluo":c.avaluo, "mutuo_sugerido":c.mutuo_sugerido, "mutuo":c.mutuo})
		respuesta.append({"lista":lista})
		
		ref_aux_oro=fn_calcula_refrendo(mutuo_oro,1)
		ref_aux_plata=fn_calcula_refrendo(mutuo_plata,2)
		ref_aux_varios=fn_calcula_refrendo(mutuo_varios,3)

		print(cont_movs)

		respuesta.append({"avaluo_oro":avaluo_oro,"avaluo_plata":avaluo_plata,"avaluo_varios":avaluo_varios,"mutuo_oro":mutuo_oro,"mutuo_plata":mutuo_plata,"mutuo_varios":mutuo_varios,"refrendo_oro":math.ceil(ref_aux_oro[0]["refrendo"]),"refrendo_plata":math.ceil(ref_aux_plata[0]["refrendo"]),"refrendo_varios":math.ceil(ref_aux_varios[0]["refrendo"])})
		respuesta.append({"cont_movs":str(cont_movs)})
	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al guardar la cotizacion."})

	return Response(respuesta)

@api_view(['GET'])
def api_limpia_cotizacion(request):
	id_usuario=request.GET.get("id_usuario")
	respuesta=[]

	try:
		respuesta.append({"estatus":"1"})
		usuario=User.objects.get(id=id_usuario)
		et=Empenos_Temporal.objects.filter(usuario=usuario)
		for x in et:
			if x.tipo_producto.id==1 or x.tipo_producto.id==2:
				Joyeria_Empenos_Temporal.objects.get(empeno_temporal=x).delete()
		et.delete()
	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al eliminar la cotizacion."})		
	return Response(respuesta)

@api_view(['GET'])
def api_elimina_producto_cotizacion(request):
	respuesta=[]
	id_producto=request.GET.get("id_producto")

	try:
		respuesta.append({"estatus":"1"})
		e=Empenos_Temporal.objects.get(id=id_producto)
		if e.tipo_producto.id==1 or e.tipo_producto.id==2:
			Joyeria_Empenos_Temporal.objects.get(empeno_temporal=e).delete()
		e.delete()

	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al eliminar el producto."})
	return Response(respuesta)

@api_view(['GET'])
def api_consulta_cliente(request):
	palabra=request.GET.get("palabra").upper()
	respuesta=[]
	try:
		respuesta.append({"estatus":"1"})
		lista=[]
		clientes=Cliente.objects.filter(nombre__contains=palabra) | Cliente.objects.filter(apellido_p__contains=palabra) | Cliente.objects.filter(apellido_m__contains=palabra)
		for c in clientes:
			lista.append({"id":c.id,"nombre":c.nombre+' '+c.apellido_p+' '+c.apellido_m,"telefono_fijo":c.telefono_fijo,"telefono_celular":c.telefono_celular})
		respuesta.append({"lista":lista})
	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al consultar los clientes."})
	return Response(respuesta)

@api_view(['GET'])
def api_consulta_boleta(request):
	print("entro")
	respuesta=[]
	id_boleta=request.GET.get("id_boleta")
	try:

		respuesta.append({"estatus":"1"})
		boleta=Boleta_Empeno.objects.get(id=id_boleta)

		#informacion de cliente
		respuesta.append({"id_plazo":boleta.plazo.id,"id_estatus_boleta":boleta.estatus.id,"cliente":boleta.cliente.nombre+' '+boleta.cliente.apellido_p+' '+boleta.cliente.apellido_m,"sucursal":boleta.sucursal.sucursal,"no_boleta":boleta.folio,"calle":boleta.cliente.calle,"CP":boleta.cliente.codigo_postal,"no_int":boleta.cliente.numero_interior,"no_ext":boleta.cliente.numero_exterior,"colonia":boleta.cliente.colonia,"ciudad":boleta.cliente.ciudad,"estado":boleta.cliente.estado,"pais":boleta.cliente.pais,"telefono_fijo":boleta.cliente.telefono_fijo,"telefono_celular":boleta.cliente.telefono_celular})
		#informacion de boleta
		respuesta.append({"tipo_producto":boleta.tipo_producto.tipo_producto,"avaluo":boleta.avaluo,"mutuo":boleta.mutuo,"refrendo":boleta.refrendo,"fecha_emision":str(boleta.fecha.strftime('%d/%m/%Y')),"fecha_vencimiento":str(boleta.fecha_vencimiento.strftime('%d/%m/%Y')),"cotitular":boleta.nombre_cotitular+' '+boleta.apellido_p_cotitular+' '+boleta.apellido_m_cotitular,"estatus":boleta.estatus.estatus})

		#buscamos los pagos de la boleta
		pagos=Pagos.objects.filter(boleta=boleta).order_by("-fecha_vencimiento")
		lista=[]

		for x in pagos:
			if x.fecha_pago==None:
				fecha_pago=" "
			else:
				fecha_pago=x.fecha_pago.strftime('%d/%m/%Y')	
			lista_periodos=[]
			periodos=Periodo.objects.filter(pago=x).order_by("-fecha_vencimiento")	
			for y in periodos:
				fecha_pago_p=" "
				if y.fecha_pago==None:
					fecha_pago_p=" "
				else:
					fecha_pago_p=y.fecha_pago.strftime('%d/%m/%Y')	
				lista_periodos.append({"tipo_pago":str(y.consecutivo)+" Refrendo Parcial","fecha_vencimiento":y.fecha_vencimiento.strftime('%d/%m/%Y'),"importe":y.importe,"fecha_pago":fecha_pago_p,"vencido":y.vencido,"pagado":y.pagado})


			lista.append({"tipo_pago":x.tipo_pago.tipo_pago,"fecha_vencimiento":x.fecha_vencimiento.strftime('%d/%m/%Y'),"importe":x.importe,"fecha_pago":fecha_pago,"vencido":x.vencido,"pagado":x.pagado,"lista_periodos":lista_periodos})

		respuesta.append({"lista":lista})
		
		det_bol=Det_Boleto_Empeno.objects.filter(boleta_empeno=boleta)
		lista_2=[]
		for x in det_bol:
			lista_2.append({"descripcion":x.descripcion,"avaluo":x.avaluo,"mutuo":x.mutuo})

		respuesta.append({"lista_2":lista_2})
		

	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al consultar la boleta."})

	return Response(respuesta)

@api_view(['GET'])
def api_reg_costo_reimpresion(request):
	print("entro a api")
	respuesta=[]
	try:
		
		id_boleta=request.GET.get("id_boleta")
		id_caja=request.GET.get("id_caja")
		costo_reimpresion=Costo_Extra.objects.get(id=1)
		caja=Cajas.objects.get(id=id_caja)
		boleta=Boleta_Empeno.objects.get(id=id_boleta)

		reg=Reg_Costos_Extra()
		reg.costo_extra=costo_reimpresion		
		reg.caja=caja
		reg.importe=costo_reimpresion.costo
		reg.boleta=boleta
		reg.save()
		respuesta.append({"estatus":"1"})
	except:
		respuesta=[]
		respuesta.append({"estatus":"0",msj:"Error al reimprimir la boleta."})
	return Response(respuesta)

#simula refrendo mensual
@api_view(['GET'])
def api_simula_refrendo_mensual(request):
	respuesta=[]
	try:
		sucursal=Sucursal.objects.get(id=int(request.GET.get("id_sucursal")))
		hoy=datetime.now()#fecha actual
		hoy=datetime.combine(hoy, time.min)
		usuario=User.objects.get(username=request.GET.get("username"))
		boleta=Boleta_Empeno.objects.get(folio=int(request.GET.get("folio_boleta")),sucursal=sucursal)
		importe_abono=request.GET.get("importe")
		numero_refrendos=request.GET.get("numero_refrendos")
		comision_pg=int(round(decimal.Decimal(request.GET.get("comision_pg"))))

		descuento_comision_pg=int(round(decimal.Decimal(request.GET.get("descuento_comision_pg"))))

		Periodo_Temp.objects.filter(usuario=usuario).delete()
		periodos=Periodo.objects.filter(boleta=boleta,pagado="N")


		for p in periodos:
			per=Periodo_Temp()
			per.usuario=usuario
			per.consecutivo=p.consecutivo
			per.boleta=p.boleta
			per.fecha_vencimiento=p.fecha_vencimiento
			per.importe=p.importe
			per.tipo_periodo=p.tipo_periodo
			per.pago=p.pago
			per.fecha_pago=p.fecha_pago
			per.vencido=p.vencido
			per.pagado=p.pagado
			per.save()

		periodos=Periodo_Temp.objects.filter(usuario=usuario).order_by("fecha_vencimiento")

		fecha_vencimiento=boleta.fecha_vencimiento
		mutuo=boleta.mutuo

		importe_abono=int(importe_abono)-(int(comision_pg)-descuento_comision_pg)

		#liquidamos los periodos.
		for p in periodos:
			if decimal.Decimal(importe_abono)>=decimal.Decimal(p.importe):
				p.pagado="S"
				p.save()

				residuo=p.consecutivo%4

				#si residuo es cero, esque  es el cuarto periodo de algun mes,
				# y la fecha de vencimiento se calcula en base a la fecha de vencimiento.
				if residuo==0:
					boleta=p.boleta
					refrendo=Tipo_Pago.objects.get(id=1)
					refrendopg=Tipo_Pago.objects.get(id=3)

					#calculamos el numero de meses
					meses_agregar=int((p.consecutivo/4)+1)

					fecha_emision=datetime.combine(p.boleta.fecha, time.min)					

					fecha_vencimiento=fn_add_months(fecha_emision,meses_agregar)

				else:
					#se calcula la nueva fecha de vencimiento.
					fecha_vencimiento=fn_add_months(p.fecha_vencimiento,1)

				importe_abono=decimal.Decimal(importe_abono)-decimal.Decimal(p.importe)

			
		importe_abono=int(round(importe_abono))

		cont_periodos_vencidos=Periodo_Temp.objects.filter(usuario=usuario,pagado="N").count()

		if int(cont_periodos_vencidos)==0:
			if int(importe_abono)>0 :			
				mutuo=mutuo-int(importe_abono)

		#por los redondeos aplicados en el formulario, puede darse el caso de que el mutuo termine con importe menor a cero.
		if mutuo<0:
			mutuo=0

		
		fecha_vencimiento=datetime.combine(fecha_vencimiento, time.min)

		#validamos que la fecha de vencimiento no sea dia de asueto.
		fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

		if mutuo==0:
			estatus_boleta="Desempeñada"			
		else:
			if fecha_vencimiento<hoy:
				estatus_boleta="Almoneda"
			elif fecha_vencimiento==hoy:
				estatus_boleta="Abierta"
			else:
				estatus_boleta="Abierta"

		respuesta.append({"estatus":"1","msj":""})
		respuesta.append({"fecha_vencimiento":fecha_vencimiento.strftime('%d/%m/%Y'),"nuevo_mutuo":mutuo,"estatus":estatus_boleta})
		periodos=Periodo_Temp.objects.filter(usuario=usuario,pagado="N").order_by("-fecha_vencimiento")

		lista=[]
		for p in periodos:
			lista.append({"fecha_vencimiento":p.fecha_vencimiento.strftime('%d/%m/%Y'),"importe":p.importe})
		respuesta.append({"lista":lista})
	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al simular el refrendo."})

	return Response(respuesta)


#Buscamos las sucursales alas que tiene acceso un usuario
@api_view(['GET'])
def api_consulta_sucurales_usuario(request):
	respuesta=[]


	
	try:
		print(request.GET.get("id"))
		user_id=request.GET.get("id")
		user=User.objects.get(id=user_id)
	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"El usuario no existe."})
		return Response(respuesta)

	try:



		pub_date = date.today()
		min_pub_date_time = datetime.combine(pub_date, time.min) 
		max_pub_date_time = datetime.combine(pub_date, time.max)  

		#validamos si el usuario tiene caja abierta en el dia actual.
		caja=Cajas.objects.filter(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=user)

		if caja.exists():			
			respuesta.append({"estatus":"0","msj":"El usuario cuenta con caja abierta, no puede cambiar de sucursal."})			

	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al consultar las sucursales."})
		return Response(respuesta)

	try:

		respuesta.append({"estatus":"1","msj":""})
		sucursales=Sucursales_Regional.objects.filter(user=user)

		lista=[]
		if sucursales.exists():
			#obtanemos las sucursales a lasque tiene acceso el usuario.
			for s in sucursales:
				lista.append({"id_sucursal":s.sucursal.id,"sucursal":s.sucursal.sucursal})
			respuesta.append({"lista":lista})

			u2=User_2.objects.get(user=user)

			#buscamos la sucursal actual.
			respuesta.append({"id_sucursal_actual":u2.sucursal.id})

		else:
			respuesta=[]
			respuesta.append({"estatus":"0","msj":"Error al consultar las sucursales."})
			return Response(respuesta)

	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al consultar las sucursales."})

		return Response(respuesta)

	return Response(respuesta)

#simula refrendo semanal
@api_view(['GET'])
def api_simula_refrendo(request):	
	respuesta=[]
	est_comisionpg=Tipo_Pago.objects.get(id=2)
	sucursal=Sucursal.objects.get(id=int(request.GET.get("id_sucursal")))
	usuario=User.objects.get(username=request.GET.get("username"))
	boleta=Boleta_Empeno.objects.get(folio=int(request.GET.get("folio_boleta")),sucursal=sucursal)
	importe_abono=request.GET.get("importe")



	#limpiamos la tabla de pagos_temp para agregar los nuevos
	Pagos_Temp.objects.filter(usuario=usuario).delete()

	#obtenemos todos los pagos no pagados.
	pagos=Pagos.objects.filter(boleta=boleta,pagado="N")

	for p in pagos:
		print(str(p.boleta)+str(p.fecha_vencimiento)+str(p.tipo_pago))
		npt=Pagos_Temp()
		npt.usuario=usuario
		npt.tipo_pago=p.tipo_pago
		npt.boleta=p.boleta
		npt.fecha_vencimiento=p.fecha_vencimiento
		npt.almacenaje=p.almacenaje
		npt.interes=p.interes
		npt.iva=p.iva
		npt.importe=p.importe
		npt.vencido=p.vencido
		npt.fecha_pago=p.fecha_pago
		npt.pagado=p.pagado
		npt.save()


	if int(importe_abono)>0:
		nuevo_mutuo=fn_simula_refrendo(importe_abono,usuario,boleta,0)

	

	pt=Pagos_Temp.objects.filter(usuario=usuario,pagado="S").exclude(tipo_pago=est_comisionpg)
	#obtenemos cuantos pagos afecto el abono.
	cont=0
	for x in pt:
		cont=cont+1
		

	pt=Pagos_Temp.objects.filter(usuario=usuario).exclude(tipo_pago=est_comisionpg).order_by("fecha_vencimiento")
	#como al afectar pagos, primero afecta a refrendos pg, y posterior mente a refrendos,
	#en este ciclo reajustamos la forma en que afecto para que primero afecte a los refrendos y despues a los refrendos pg
	#si nando comenta que srequiere que primero se afecten a los refrendos pg, solo hay qu quitar este ciclo.
	if cont>0:
		for x in pt:
			x.pagado="N"
			x.save()
			if cont>0:
				x.pagado="S"
				x.save()
			cont=cont-1

			
	pagos_t=Pagos_Temp.objects.filter(usuario=usuario,pagado="N").order_by("-fecha_vencimiento")


	lista=[]
	for pt in pagos_t:
		
		lista.append({"importe":str(pt.importe),"fecha_vencimiento":pt.fecha_vencimiento.strftime('%d/%m/%Y'),"vencido":pt.vencido,"pagado":pt.pagado})
	respuesta.append({"lista":lista})


	respuesta.append({"nuevo_mutuo":nuevo_mutuo})

	return Response(respuesta)















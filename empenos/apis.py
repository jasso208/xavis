from rest_framework.response import Response

from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny 

from empenos.models import Tipo_Producto,Linea,Sub_Linea,Marca,Costo_Kilataje,Empenos_Temporal,Joyeria_Empenos_Temporal,Cliente,Boleta_Empeno
from empenos.models import Pagos,Det_Boleto_Empeno,Periodo_Temp
from django.contrib.auth.models import User

import math
from empenos.funciones import *
from django.core import serializers
from empenos.jobs import *
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
import json
from django.db import transaction

#api para establecer el precio de venta y apartado fijo
@api_view(["PUT","GET"])
def api_precio_venta_fijo(request):
	resp = []
	if request.method == "PUT":


		id_sucursal = request.data["id_sucursal"]
		folio_boleta = request.data["folio_boleta"]
		id_usuario = request.data["id_usuario"]

		importe = request.data["importe"]
		
		try:
			boleta = Boleta_Empeno.objects.get(sucursal__id = int(id_sucursal),folio = folio_boleta)
			re = boleta.fn_establece_precio_venta_y_apartado(importe,id_usuario)
			if re[0]:
				resp.append({"estatus":"1"})
			else:
				resp.append({"estatus":"0","msj":"Error al actualizar la información."})
		except Exception as e:
			print("api_establace_precio_venta" + str(e))
			resp.append({"estatus":"0","msj":"Error al actualizar la información."})
	elif request.method == "GET":
		id_sucursal = request.GET.get("id_sucursal")
		folio_boleta = request.GET.get("folio_boleta")

		try:
			boleta = Boleta_Empeno.objects.get(sucursal__id = int(id_sucursal),folio = folio_boleta)

			resp.append({"estatus":"1","importe":str(math.ceil(boleta.fn_calcula_precio_venta()))})
		except Exception as e:
			print("api_establace_precio_venta" + str(e))
			resp.append({"estatus":"0","msj":"La boleta indicada no existe."})

	return Response(json.dumps(resp))


#api para cancelar abono semanal
@api_view(["PUT"])
def api_cancela_abono(request):
	id_abono = request.data["id_abono"]
	id_usuario = request.data["id_usuario"]

	usuario = User.objects.get(id = int(id_usuario))
	user_2 = User_2.objects.get (user = usuario)

	if user_2.perfil.id != 3:
		respuesta.append({"estatus":"0","msj" : "El usuario no tiene permiso para cancelar el abono."})
		return Response(json.dumps(respuesta))

	abono = Abono.objects.get(id = int(id_abono))

	resp = abono.fn_cancela_abono(usuario)

	respuesta = []
	if len(resp) == 0:
		respuesta.append({"estatus":"1"})#se cancelo correctamente
	else:
		respuesta.append({"estatus":"0","msj":resp[1]})

	return Response(json.dumps(respuesta))

#api para aplicar los refrendos semanales.
#regresa el id del abono que se acaba de aplicar.
@api_view(["POST"])
@transaction.atomic
def api_aplica_refrendo_semanal(request):
	"""
		Parametros
	"""

	id_boleta = request.data["id_boleta"]
	numero_semanas_a_pagar = request.data["numero_semanas_a_pagar"]
	comision_pg = request.data["comision_pg"]
	descuento_comision_pg = request.data["descuento_comision_pg"]
	id_usuario = request.data["id_usuario"]
	importe_abono = request.data["importe_abono"]
	id_caja = request.data["id_caja"]
	importe_capital = request.data["importe_capital"]

	"""
		Parametros
	"""
	respuesta = []

	usuario = User.objects.get(id = int(id_usuario))
	boleta = Boleta_Empeno.objects.get(id = int(id_boleta))
	caja = Cajas.objects.get(id = int(id_caja))

	tm=Tipo_Movimiento.objects.get(id=5)
	folio=fn_folios(tm,boleta.sucursal)

	#creamos el abono
	abono=Abono()
	abono.usuario=usuario
	abono.importe=importe_abono
	abono.caja=caja
	abono.boleta=boleta
	abono.folio=folio
	abono.tipo_movimiento=tm
	abono.sucursal=boleta.sucursal
	abono.save()

	

	#esta informacion es necesaria para en caso de cancelar el refrendo.
	boleta.estatus_anterior = boleta.estatus
	boleta.fecha_vencimiento_anterior = boleta.fecha_vencimiento
	boleta.fecha_vencimiento_real_anterior = boleta.fecha_vencimiento_real
	boleta.save()
	
	importe_a_pagos = float(importe_abono) - (float(comision_pg) - float(descuento_comision_pg))

	#si la funcion regreso false es porque fallo
	if float(comision_pg) > 0:
		rcpg = boleta.fn_paga_comision_pg(descuento_comision_pg,abono)
		if not rcpg[0]:
			respuesta.append({"estatus":"0","msj":rcpg[1]})
			transaction.set_rollback(True)
			return Response(json.dumps(respuesta))
	
	if int(numero_semanas_a_pagar) > 0:
		resp_pagos = boleta.fn_salda_pagos(int(numero_semanas_a_pagar),importe_a_pagos,abono)
		if not resp_pagos[0]:
			respuesta.append({"estatus":"0","msj":resp_pagos[1]})
			transaction.set_rollback(True)
			return Response(json.dumps(respuesta))
	
	if int(importe_capital) > 0:
		if not boleta.fn_abona_capital(int(importe_capital),abono):
			respuesta.append({"estatus":"0","msj":"Error al aplicar el abono a capital."})
			transaction.set_rollback(True)
			return Response(json.dumps(respuesta))
	
	ia=Imprime_Abono()
	ia.usuario=usuario
	ia.abono=abono
	ia.save()

	respuesta = []
	respuesta.append({"estatus":"1"})

	return Response(json.dumps(respuesta))


@api_view(["GET"])
def api_simula_proximos_pagos_semanal(request):

	simulacion = []
	try:		
		simulacion.append({"estatus":"1"})
		id_boleta = request.GET.get("id_boleta")
		abono_capital = float(request.GET.get("abono_capital"))

		semanas_a_refrendar = request.GET.get("semanas_a_refrendar")
		boleta = Boleta_Empeno.objects.get(id = int(id_boleta))
		simulacion.append(boleta.fn_simula_proximos_pagos(int(semanas_a_refrendar)))

		

		refrendo_semanal =round(float(boleta.fn_simula_calcula_refrendo(boleta.mutuo - abono_capital)[0]["refrendo"])/4.00)
		if refrendo_semanal == 0 and int(boleta.mutuo - abono_capital)>0:
			refrendo_semanal = 1
		simulacion.append({"nuevo_mutuo":boleta.mutuo - abono_capital,"refrendo_semanal":refrendo_semanal})
	except Exception as e:
		print(e)
		simulacion = []
		simulacion.append({"estatus":"0"})

	return Response(json.dumps(simulacion))


@api_view(["GET"])
def api_cliente(request):

	id_cliente = request.GET.get("id_cliente")
	cliente = Cliente.objects.filter(id=id_cliente).values("nombre","apellido_p","apellido_m")
	return Response(cliente)



@api_view(["GET"])
def api_porcentaje_mutuo(request):
	respuesta=[]
	id_sucursal = request.GET.get("id_sucursal")
	sucursal = Sucursal.objects.get(id = int(id_sucursal))

	resp = sucursal.fn_consulta_porcentaje_mutuo()

	#si el valor que nos regreso es boleano, es porque no se encontro la configuracion del mutuo.
	if type(resp) == type(False):
		porcentaje_oro = 0.00
		porcentaje_plata = 0.00
		porcentaje_articulos_varios = 0.00
	else:
		porcentaje_oro = resp.porcentaje_oro
		porcentaje_plata = resp.porcentaje_plata
		porcentaje_articulos_varios = resp.porcentaje_articulos_varios

	respuesta.append({"porcentaje_oro":porcentaje_oro,"porcentaje_plata":porcentaje_plata,"porcentaje_articulos_varios":porcentaje_articulos_varios})

	return Response(respuesta)

@api_view(["GET"])
def api_consulta_configuracion_empeno(request):
	respuesta = []
	try:
		id_sucursal = request.GET.get("id_sucursal")
		sucursal = Sucursal.objects.get(id=int(id_sucursal))

		resp_interes = Configuracion_Interes_Empeno.fn_get_configuracion_interes_empeno(sucursal)

		print(resp_interes)
		#si el tipo de dato es boletano y como solo podemos regresar false o un queryset,
		#asumimos que fallo.
		if type(resp_interes) == type(False):
			respuesta.append({"almacenaje_oro":"0.00","interes_oro":"0.00","iva_oro":"0.00","almacenaje_plata":"0.00","interes_plata":"0.00","iva_plata":"0.00","almacenaje_prod_varios":"0.00","interes_prod_varios":"0.00","iva_prod_varios":"0.00"})
		else:
			respuesta.append({"almacenaje_oro":resp_interes.almacenaje_oro,"interes_oro":resp_interes.interes_oro,"iva_oro":resp_interes.iva_oro,"almacenaje_plata":resp_interes.almacenaje_plata,"interes_plata":resp_interes.interes_plata,"iva_plata":resp_interes.iva_plata,"almacenaje_prod_varios":resp_interes.almacenaje_prod_varios,"interes_prod_varios":resp_interes.interes_prod_varios,"iva_prod_varios":resp_interes.iva_prod_varios})

	except Exception as e:
		print(e)
		respuesta.append({"almacenaje_oro":"0.00","interes_oro":"0.00","iva_oro":"0.00","almacenaje_plata":"0.00","interes_plata":"0.00","iva_plata":"0.00","almacenaje_prod_varios":"0.00","interes_prod_varios":"0.00","iva_prod_varios":"0.00"})
	return Response(respuesta)


@api_view(["PUT"])
def api_cancela_retiro(request):
	respuesta = []

	try:

		id_usuario = request.data["id_usuario"]
		comentario = request.data["comentario"]
		id_retiro = request.data["id_retiro"]

		retiro = Retiro_Efectivo.objects.get(id = int(id_retiro))

		resp = retiro.fn_cancela_retiro(id_usuario,comentario)

		if resp:
			respuesta.append({"estatus":"1"})
		else:
			respuesta.append({"estatus":"0","msj":"Error al cancelar el retiro."})			

	except Exception as e:		

		respuesta.append({"estatus":"0","msj":"Error al cancelar el retiro."})

	return Response(respuesta)


#validamos si el concepto que se selecciono para el retiro puede cubrir el importe
#que se desea retirar.
@api_view(['GET'])
def api_valida_importe_retiro(request):
	respuesta = []
	try:	
		importe_a_retirar = request.GET.get("importe_a_retirar")
		id_concepto_retiro = request.GET.get("id_concepto_retiro")

		saldo_concepto = Concepto_Retiro.objects.get(id = int(id_concepto_retiro)).fn_saldo_concepto()		

		if int(saldo_concepto) >= int(importe_a_retirar):	
			respuesta.append({"estatus" : "1"})
		else:
			respuesta.append({"estatus" : "0","msj" : "El concepto seleccionado no cuenta con saldo suficiente para hacer el retiro. Saldo concepto: " + str(saldo_concepto)})

	except Exception as e:		
		respuesta = []
		respuesta.append({"estatus" : "0","msj" : "Error al validar el saldo del concepto de retiro."})

	return Response(respuesta)


@api_view(['POST','GET','DELETE','PUT'])
@transaction.atomic
def api_concepto_retiro(request):
	
	respuesta=[]
	if request.method=="POST":
		
		try:
			concepto = request.data["concepto"]
			id_usuario = request.data["id_usuario"]
			importe = request.data["importe"]
			id_sucursal = request.data["id_sucursal"]


			resp = Concepto_Retiro.fn_nuevo_concepto(id_sucursal,id_usuario,importe,concepto)
			if resp:				
				respuesta.append({"estatus":"1"})
			else:
				respuesta.append({"estatus":"0","msj":"Error al guardar el nuevo concepto"})

		except Exception as e:
			respuesta.append({"estatus":"0","msj":"Error al guardar el nuevo concepto"})
	if request.method == "GET":
		respuesta = []
		try:
			lista = []
			id_sucursal = request.GET.get("id_sucursal")
			resp = Concepto_Retiro.fn_get_conceptos(id_sucursal)
		
			for r in resp:
				importe_maximo_retiro = "{:0,.2f}".format(r.importe_maximo_retiro)
				lista.append({"id_concepto" : r.id,"concepto" : r.concepto,"importe_maximo" : importe_maximo_retiro})

			respuesta.append({"estatus" : "1"})
			respuesta.append({"lista" : lista})
		except:
			respuesta.append({"estatus" : "0","msj" : "Error al consultar los conceptos de la sucursal."})
	if request.method == "DELETE":
		id_concepto = request.data["id_concepto"]
		id_usuario = request.data["id_usuario"]

		try:

			resp = Concepto_Retiro.fn_delete_concepto(id_concepto,id_usuario);	



			if resp:				
					respuesta.append({"estatus" : "1"})
			else:
				respuesta.append({"estatus" : "0","msj" : "Error al eliminar el concepto"})
				
		except:
			respuesta.append({"estatus" : "0","msj" : "Error al eliminar el concepto"})
			

	if request.method == "PUT":
		id_concepto = request.data["id_concepto"]
		id_usuario = request.data["id_usuario"]
		importe_maximo_retiro = request.data["importe_maximo_retiro"]

		try:
			resp = Concepto_Retiro.fn_update_importe_maximo_retiro(id_concepto,importe_maximo_retiro,id_usuario)
			if resp:

				saldo = Concepto_Retiro.objects.get( id = int(id_concepto)).fn_saldo_concepto()

				if saldo < 0:
					
					respuesta.append({"estatus" : "0","msj" : "El importe indicado no es valido. Durante el mes actual se ha retirado mas de esta cantidad."})
					transaction.set_rollback(True)
				else:
					respuesta.append({"estatus":"1"})
			else:
				respuesta.append({"estatus":"0","msj":"Error al actualizar el importe maximo de retiro del concepto."})
		except Exception as e:
			print(e)
			respuesta.append({"estatus":"0","msj":"Error al actualizar el importe maximo de retiro del concepto."})

	return Response(respuesta)


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
def api_consulta_cliente_2(request):
	respuesta=[]
	try:
		

		id=request.GET.get("id")
		cliente=Cliente.objects.get(id=id)
		respuesta.append({"cliente":cliente.nombre+' '+cliente.apellido_p+' '+cliente.apellido_m})


	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({'estatus':"0",'msj':"Error al consultar el cliente."})#estatus de falla

	return Response(respuesta)


@api_view(['GET'])
def api_limpia_venta_piso(request):
	respuesta=[]
	try:

		username=request.GET.get("username")
		usuario=User.objects.get(username=username)

		Venta_Temporal_Piso.objects.filter(usuario=usuario).delete()
		respuesta.append({"estatus":"1"})

	except Exception as e:
		respuesta=[]
		print(e)
		respuesta.append({"estatus":"0","msj":"Error al limpiar la cotización."})
	return Response(respuesta)


@api_view(['GET'])
def api_elimina_prod_apartado(request):
	respuesta=[]
	try:
		id=int(request.GET.get("id"))
		Apartado_Temporal.objects.get(id=id).delete()
		respuesta.append({"estatus":"1"})
	except Exception as e:
		respuesta=[]
		print(e)
		respuesta.append({"estatus":"0","msj":"Error al eliminar el producto."})
	return Response(respuesta)


@api_view(['GET'])
def api_elimina_prod_venta_piso(request):
	respuesta=[]
	try:
		id=int(request.GET.get("id"))
		Venta_Temporal_Piso.objects.get(id=id).delete()
		respuesta.append({"estatus":"1"})
	except Exception as e:
		respuesta=[]
		print(e)
		respuesta.append({"estatus":"0","msj":"Error al eliminar el producto."})
	return Response(respuesta)


@api_view(['GET'])
def api_consulta_prod_temporal_apartado(request):
	respuesta=[]

	try:

		username=request.GET.get("username")

		usuario=User.objects.get(username=username)
		
		#buscamos porcentaje sobre apartado
		cont=Porcentaje_Sobre_Avaluo.objects.all().count()

		#si cont es diferente de 1 es porque el porcentaje que se agregara sobre avaluo para calcular el precio de producto
		#esta incorrecto
		if cont!=1:			
			respuesta.append({"estatus":"0","msj":"Error al consultar los productos."})
			return Response(respuesta)


		porcentaje=Porcentaje_Sobre_Avaluo.objects.all().aggregate(Sum("porcentaje_apartado"))

		porce=0;
		if porcentaje["porcentaje_apartado__sum"]!=None:
			porce=int(porcentaje["porcentaje_apartado__sum"])

		

		at=Apartado_Temporal.objects.filter(usuario=usuario).order_by("boleta")

		total_mutuo=0.00
		total_avaluo=0.00
		total_pagar=0.00

		lista=[]

		for v in at:
			db=Det_Boleto_Empeno.objects.filter(boleta_empeno=v.boleta)
			descripcion=""

			for d in db:
				if d.observaciones==None:
					ob=""
				else:
					ob=d.observaciones

				descripcion=descripcion+d.descripcion+", "+ob+"; "

			total=math.ceil(v.boleta.fn_calcula_precio_apartado())#decimal.Decimal(d.avaluo)+(decimal.Decimal(d.avaluo)*(decimal.Decimal(porce)/decimal.Decimal(100.00)))

			#trabajamos con el mutuo de la boleta no con el mutuo origina, ya que para fines de utilidad, nos barsaremos en lo que realmene se le dio al cliente.
			total_mutuo=decimal.Decimal(total_mutuo)+decimal.Decimal(v.boleta.mutuo)
			total_avaluo=decimal.Decimal(total_avaluo)+decimal.Decimal(v.boleta.avaluo)
			total_pagar=math.ceil(decimal.Decimal(total_pagar)+decimal.Decimal(v.boleta.fn_calcula_precio_apartado()))

			total="{:0,.2f}".format(total)
			mutuo="{:0,.2f}".format(v.boleta.mutuo)
			avaluo="{:0,.2f}".format(v.boleta.avaluo)

			lista.append({"id":v.id,"descripcion":descripcion,"folio":v.boleta.folio,"estatus":v.boleta.estatus.estatus,"tipo_producto":v.boleta.tipo_producto.tipo_producto,"avaluo":avaluo,"mutuo":mutuo,"total":str(total)})

		respuesta.append({"estatus":"1"})
		respuesta.append({"lista":lista})


		try:
			ma=Min_Apartado.objects.get(id=1)
		except Exception as e:
			respuesta.append({"estatus":"0","msj":"No se ha capturado el minimo para apartado."})
			return Response(respuesta)

		min_apartado_1_mes=math.ceil(decimal.Decimal(total_pagar)*(decimal.Decimal(ma.porc_min_1_mes)/decimal.Decimal(100)))
		min_apartado_2_mes=math.ceil(decimal.Decimal(total_pagar)*(decimal.Decimal(ma.porc_min_2_mes)/decimal.Decimal(100)))


		intmin_apartado_1_mes=int(min_apartado_1_mes)
		intmin_apartado_2_mes=int(min_apartado_2_mes)

		inttotal_pagar=total_pagar

		total_mutuo="{:0,.2f}".format(total_mutuo)
		total_avaluo="{:0,.2f}".format(total_avaluo)
		total_pagar="{:0,.2f}".format(total_pagar)

		min_apartado_1_mes="{:0,.2f}".format(min_apartado_1_mes)		
		min_apartado_2_mes="{:0,.2f}".format(min_apartado_2_mes)

		respuesta.append({"intmin_apartado_2_mes":intmin_apartado_2_mes,"intmin_apartado_1_mes":intmin_apartado_1_mes,"min_apartado_1_mes":min_apartado_1_mes,"min_apartado_2_mes":min_apartado_2_mes,"total_mutuo":total_mutuo,"total_avaluo":total_avaluo,"total_pagar":total_pagar,"inttotal_pagar":inttotal_pagar})

	except Exception as e:
		respuesta=[]
		print(e)
		respuesta.append({"estatus":"0","msj":"Error al consultar los productos."})

	return Response(respuesta)



@api_view(['GET'])
def api_consulta_prod_temporal_piso(request):
	respuesta=[]
		
	

	try:

		username=request.GET.get("username")

		usuario=User.objects.get(username=username)
		
		cont=Porcentaje_Sobre_Avaluo.objects.all().count()


		#si cont es diferente de 1 es porque el porcentaje que se agregara sobre avaluo para calcular el precio de producto
		#esta incorrecto
		if cont!=1:			
			respuesta.append({"estatus":"0","msj":"Error al consultar los productos."})
			return Response(respuesta)


		porcentaje=Porcentaje_Sobre_Avaluo.objects.all().aggregate(Sum("porcentaje"))

		porce=0;
		if porcentaje["porcentaje__sum"]!=None:
			porce=decimal.Decimal(porcentaje["porcentaje__sum"])

		

		vtp=Venta_Temporal_Piso.objects.filter(usuario=usuario).order_by("boleta")

		total_mutuo=0.00
		total_avaluo=0.00
		total_pagar=0.00

		lista=[]

		for v in vtp:
			db=Det_Boleto_Empeno.objects.filter(boleta_empeno=v.boleta)
			descripcion=""

			for d in db:
				if d.observaciones==None:
					ob=""
				else:
					ob=d.observaciones

				descripcion=descripcion+d.descripcion+", "+ob+"; "

			total = v.boleta.fn_calcula_precio_venta()#decimal.Decimal(d.avaluo)+(decimal.Decimal(d.avaluo)*(decimal.Decimal(porce)/decimal.Decimal(100.00)))

			#trabajamos con el mutuo de la boleta no con el mutuo origina, ya que para fines de utilidad, nos barsaremos en lo que realmene se le dio al cliente.
			total_mutuo=decimal.Decimal(total_mutuo)+decimal.Decimal(v.boleta.mutuo)
			total_avaluo=decimal.Decimal(total_avaluo)+decimal.Decimal(v.boleta.avaluo)
			total_pagar=decimal.Decimal(total_pagar)+decimal.Decimal(v.boleta.fn_calcula_precio_venta())

			total="{:0,.2f}".format(total)
			mutuo="{:0,.2f}".format(v.boleta.mutuo)
			avaluo="{:0,.2f}".format(v.boleta.avaluo)

			lista.append({"id":v.id,"descripcion":descripcion,"folio":v.boleta.folio,"estatus":v.boleta.estatus.estatus,"tipo_producto":v.boleta.tipo_producto.tipo_producto,"avaluo":avaluo,"mutuo":mutuo,"total":str(total)})

		respuesta.append({"estatus":"1"})
		respuesta.append({"lista":lista})

		inttotal_pagar=total_pagar

		total_mutuo="{:0,.2f}".format(total_mutuo)
		total_avaluo="{:0,.2f}".format(total_avaluo)
		total_pagar="{:0,.2f}".format(total_pagar)



		respuesta.append({"total_mutuo":total_mutuo,"total_avaluo":total_avaluo,"total_pagar":total_pagar,"inttotal_pagar":inttotal_pagar})


	except Exception as e:
		respuesta=[]
		print(e)
		respuesta.append({"estatus":"0","msj":"Error al consultar los productos."})

	return Response(respuesta)


@api_view(['GET'])
def api_agrega_prod_apartado(request):
	respuesta=[]
	try:
		
		username=request.GET.get("username")
		folio=int(request.GET.get("folio"))
		id_sucursal=int(request.GET.get("id_sucursal"))

		sucursal=Sucursal.objects.get(id=id_sucursal)

		boleta=Boleta_Empeno.objects.get(sucursal=sucursal,folio=folio)


		#si la boleta no esta en almoneda o en remate, no permitira agregarla.
		if boleta.estatus.id==3 or boleta.estatus.id==5:
			print("boleta valida")
		else:
			respuesta.append({"estatus":"0","msj":"La boleta no esta disponible para ser apartada."})
			return Response(respuesta)

		try:	
			#si la boleta ya existe en una venta, ya no puede ser apartada.
			dvp=Det_Venta_Piso.objects.get(boleta=boleta)

			respuesta.append({"estatus":"0","msj":"La boleta ya fue vendida."})
			return Response(respuesta)
		except:
			print("Boleta disponible para apartado")

		try:
			#si la bleta existe en un apartado, ya no puede ser apartada
			da=Apartado.objects.get(boleta=boleta)			
			respuesta.append({"estatus":"0","msj":"La boleta ya esta apartada."})
			return Response(respuesta)

		except:
			print("Boleta disponible para apartado")



		usuario=User.objects.get(username=username)

		vtp=Apartado_Temporal.objects.filter(boleta=boleta)

		#si existe es que ya fue agregada la boelta.
		if vtp.exists():
			respuesta.append({"estatus":"0","msj":"La boleta ya ha sido agregada."})
			return Response(respuesta)

		try:
			at=Apartado_Temporal.objects.get(usuario=usuario)
			respuesta.append({"estatus":"0","msj":"Solo puedes apartar un producto por ticket."})
			return Response(respuesta)			
		except:
			print("")


		Apartado_Temporal.objects.create(usuario=usuario,boleta=boleta)
		respuesta.append({"estatus":"1"})
		print(respuesta);
	except Exception as e:
		print(e)
		print("fallo")
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al agregar el producto."})

	return Response(respuesta)


@api_view(['GET'])
def api_agrega_prod_venta_piso(request):
	respuesta=[]
	try:
		
		username=request.GET.get("username")
		folio=int(request.GET.get("folio"))
		id_sucursal=int(request.GET.get("id_sucursal"))

		sucursal=Sucursal.objects.get(id=id_sucursal)

		boleta=Boleta_Empeno.objects.get(sucursal=sucursal,folio=folio)


		#si la boleta no esta en almoneda o en remate, no permitira agregarla.
		if boleta.estatus.id==3 or boleta.estatus.id==5:
			print("boleta valida")
		else:
			respuesta.append({"estatus":"0","msj":"La boleta no esta disponible para la venta."})
			return Response(respuesta)

		try:	
			#si la boleta ya esta incluida en una venta, ya no puede ser vendida
			dvp=Det_Venta_Piso.objects.get(boleta=boleta)
			
			return Response(respuesta)
		except Exception as e:
			print(e)
			print("boleta_valida para venta")


		try:
			#si la bleta existe en un apartado, ya no puede ser apartada
			da=Apartado.objects.get(boleta=boleta)						
			respuesta.append({"estatus":"0","msj":"La boleta no esta disponible para la venta."})
			return Response(respuesta)
		except Exception as e:
			print(e)
			print("Boleta disponible para Venta")



		usuario=User.objects.get(username=username)

		vtp=Venta_Temporal_Piso.objects.filter(boleta=boleta)

		print(vtp)
		#si existe la boleta, ya no debemos agregarla nuevamente.
		if vtp.exists():
			respuesta.append({"estatus":"0","msj":"La boleta ya ha sido agregada."})
			return Response(respuesta)

		Venta_Temporal_Piso.objects.create(usuario=usuario,boleta=boleta)

		respuesta.append({"estatus":"1"})
		print(respuesta);
	except Exception as e:
		print(e)
		print("fallo")
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al agregar el producto."})

	return Response(respuesta)

@api_view(['GET'])
def api_agrega_importe_real_venta(request):
	respuesta=[]

	try:
		
		id_caja=request.GET.get("id_caja")		
		id_usuario=request.GET.get("id_usuario")		

		caja=Cajas.objects.get(id=id_caja)

		usuario=User.objects.get(id=id_usuario)


		venta=Venta_Granel.objects.get(id=int(request.GET.get("id_venta")))

		venta.importe_venta=decimal.Decimal(request.GET.get("importe"))

		venta.caja=caja

		venta.usuario_finaliza=usuario

		venta.fecha_importe_venta=timezone.now()

		venta.save()

		respuesta.append({"estatus":"1"})
		
	except Exception  as e:
		print(e)
		respuesta=[]
		respuesta.append({"estatus":"0","msj":"Error al agregar el importe."})

	return Response(respuesta)



@api_view(['GET'])
@transaction.atomic
def api_agrega_boleta_venta_granel(request):
	respuesta=[]

	try:
		id=int(request.GET.get("id"))		
		respuesta.append({'estatus':"1"})#estatus de falla
		vt=Venta_Temporal.objects.get(id=id)
		usuario=vt.usuario

		if vt.vender=="S":

			vt.vender="N"			
			
		else:
			vt.vender="S"			
			
		vt.save()

		vt2=Venta_Temporal.objects.filter(usuario=usuario,vender="S")

		avaluo=0.00
		mutuo=0.00
		for x in vt2:
			avaluo=decimal.Decimal(avaluo)+decimal.Decimal(x.boleta.avaluo)
			mutuo=decimal.Decimal(mutuo)+decimal.Decimal(x.boleta.mutuo)

		respuesta.append({'marcado':vt.vender,"avaluo":"{:0,.2f}".format(avaluo) ,"mutuo": "{:0,.2f}".format(mutuo) })

	except Exception as e:
		print(e)
		respuesta.append({'estatus':"0",'msj':"Error al agregar la boleta."})#estatus de falla

	return Response(respuesta)


@api_view(['GET'])
def api_agregar_kilataje(request):
	respuesta=[]
	try:
		kilataje=request.GET.get("desc_kilataje")
		avaluo=request.GET.get("importe")
		id_tipo_producto=request.GET.get("id_tipo_producto")
		id_tipo_kilataje=request.GET.get("id_tipo_kilataje")

		tipo_producto=Tipo_Producto.objects.get(id=int(id_tipo_producto))
		tipo_kilataje=Tipo_Kilataje.objects.get(id=int(id_tipo_kilataje))

		Costo_Kilataje.objects.create(tipo_producto=tipo_producto,kilataje=kilataje,avaluo=avaluo,tipo_kilataje=tipo_kilataje)
		respuesta.append({"estatus":"1"})
	except Exception as e:	
		print(e)
		respuesta.append({"estatus":"0","msj":"Error al agregar el nuevo kilataje."})

	return Response(respuesta)	


#no podemos eliminar los costo kilatake
#ni modificarlos, ya que pueda estar ligado a boletas.
@api_view(['GET'])
def api_elimina_costo_kilataje(request):
	respuesta=[]
	id=int(request.GET.get("id"))
	try:
		ck=Costo_Kilataje.objects.get(id=id)
		ck.activo="N"
		ck.save()

		respuesta.append({"estatus":"1"})
	except Exception as e:	
		print(e)
		respuesta.append({"estatus":"0","msj":"Error al eliminar el registro."})
	return Response(respuesta)


@api_view(['GET'])
def api_elimina_costo_extra(request):
	respuesta=[]
	id=int(request.GET.get("id"))
	try:
		Reg_Costos_Extra.objects.get(id=id).delete()
		respuesta.append({"estatus":"1"})
	except:	
		print(e)
		respuesta.append({"estatus":"0","msj":"Error al eliminar el registro."})
	return Response(respuesta)


@api_view(['GET'])
def api_agrega_marca(request):
	respuesta=[]
	try:
		marca=request.GET.get("marca").upper()
		m=Marca.objects.filter(marca=marca)		
		if m.exists():
			print("la marca ya existe")
			respuesta.append({"estatus":"0","msj":"La marca ya existe."})
		else:
			Marca.objects.create(marca=marca)
		respuesta.append({"estatus":"1"})
	except Exception as e:		
		print(e)
		respuesta.append({"estatus":"0","msj":"Error al registrar la marca."})
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
def api_backup(request):
	respuesta = []
	estatus = fn_job_backup_basededatos()
	if estatus:
		fn_envia_mail("Job respaldo base de datos exitoso","SE ejecuto correctamente","jasso.gallegos@gmail.com")
	else:
		fn_envia_mail("Job respaldo base de datos incorrecto","ERror al generar el respaldo de base de datos","jasso.gallegos@gmail.com")
	return Response(respuesta)

@api_view(['GET'])
def api_job_diario(request):
	respuesta=[]
	try:
		fn_job_diario()
		fn_envia_mail("JOB Fechas vencimiento se ejecuto correctamente","Job Vencimientos","jasso.gallegos@gmail.com")
	except Exception as e:
		fn_envia_mail(str(e),"Fallo Job Vencimientos","jasso.gallegos@gmail.com")
		
	try:
		estatus=fn_job_libera_apartado()
		if estatus:
			fn_envia_mail("JOB libera apartados se ejecuto correctamente","Job libera apartados","jasso.gallegos@gmail.com")
		else:
			fn_envia_mail("Error job libera apartados se ejecuto correctamente","Error job libera apartados","jasso.gallegos@gmail.com")

	except:
		fn_envia_mail("Error job libera apartados se ejecuto correctamente","Error job libera apartados","jasso.gallegos@gmail.com")
		
	return Response(respuesta)

@api_view(["GET"])
def api_guarda_estatus_cartera(request):
	respuesta = []
	try:
		estatus = fn_guarda_estatus_cartera()
		if estatus:
			fn_envia_mail("Exito El guardado de estatus de cartera","Exito Job guarda estatus cartera","jasso.gallegos@gmail.com")
		else:
			fn_envia_mail("Fallo el guardado de estatus de cartera","Error Job guarda estatus cartera","jasso.gallegos@gmail.com")

	except:
		fn_envia_mail(str(e),"Error Job guarda estatus cartera","jasso.gallegos@gmail.com")

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
		ck=Costo_Kilataje.objects.filter(tipo_producto=id_tipo_producto,activo="S").order_by("kilataje")
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

	respuesta = []
	id_usuario = request.GET.get("id_usuario")
	id_sucursal = request.GET.get("id_sucursal")

	sucursal = Sucursal.objects.get(id = id_sucursal)

	print("id_usuario")
	print(request.GET.get("id_usuario"))

	try:
		avaluo_oro = 0
		avaluo_plata = 0
		avaluo_varios = 0
		mutuo_oro = 0
		mutuo_plata = 0
		mutuo_varios = 0

		respuesta.append({"estatus":"1"})
		usuario = User.objects.get(id = id_usuario)


		cotizacion = Empenos_Temporal.objects.filter(usuario = usuario)
		lista = []
		cont_movs = 0

		#de los productos en la cotizacion, sumamos cuanto mutuo hay de cada tipo de producto
		#para poder calcular el refrendo total de la cotizacion.
		for c in cotizacion:
			cont_movs = cont_movs+1
			if c.tipo_producto.id == 1:
				avaluo_oro = avaluo_oro + c.avaluo
				mutuo_oro = mutuo_oro + c.mutuo
			elif c.tipo_producto.id == 2:
				avaluo_plata = avaluo_plata + c.avaluo
				mutuo_plata = mutuo_plata + c.mutuo
			elif c.tipo_producto.id == 3:
				avaluo_varios = avaluo_varios + c.avaluo
				mutuo_varios = mutuo_varios + c.mutuo
			kilataje = ""
			peso = ""

			#en caso de ser joyeria obtenemos el peso
			if c.tipo_producto.id == 1 or c.tipo_producto.id == 2:
				j = Joyeria_Empenos_Temporal.objects.get(empeno_temporal = c)
				
				kilataje = j.costo_kilataje.kilataje
				peso = j.peso

			lista.append({"id":c.id,"tipo_producto":c.tipo_producto.tipo_producto,"linea":c.linea.linea, "sub_linea":c.sub_linea.sub_linea, "marca":c.marca.marca, "descripcion":c.descripcion, "Kilataje":kilataje, "peso":peso, "avaluo":c.avaluo, "mutuo_sugerido":c.mutuo_sugerido, "mutuo":c.mutuo})
		respuesta.append({"lista":lista})
		
		ref_aux_oro = sucursal.fn_calcula_refrendo(mutuo_oro,1)
		ref_aux_plata = sucursal.fn_calcula_refrendo(mutuo_plata,2)
		ref_aux_varios = sucursal.fn_calcula_refrendo(mutuo_varios,3)

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

		Cliente.fn_actualiza_nombre_completo()


		clientes=Cliente.objects.filter(nombre_completo__contains=palabra) 
		
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
			#si es comision de pg de importe 0, no se muestra
			if x.tipo_pago.id == 2 and int(x.importe) == 0:
				pass
			else:
				lista.append({"tipo_pago":x.tipo_pago.tipo_pago,"fecha_vencimiento":x.fecha_vencimiento.strftime('%d/%m/%Y'),"importe":x.importe,"fecha_pago":fecha_pago,"vencido":x.vencido,"pagado":x.pagado,"lista_periodos":lista_periodos})
			#lista.append({"tipo_pago":x.tipo_pago.tipo_pago,"fecha_vencimiento":x.fecha_vencimiento.strftime('%d/%m/%Y'),"importe":x.importe,"fecha_pago":fecha_pago,"vencido":x.vencido,"pagado":x.pagado,"lista_periodos":lista_periodos})

		respuesta.append({"lista":lista})
		
		det_bol=Det_Boleto_Empeno.objects.filter(boleta_empeno=boleta)
		lista_2=[]
		for x in det_bol:
			if x.costo_kilataje == None:
				kilataje = ""
			else:
				kilataje = x.costo_kilataje.kilataje
			lista_2.append({"descripcion":x.descripcion,"avaluo":x.avaluo,"mutuo":x.mutuo,"peso":x.peso,"kilataje":kilataje,"mutuo":x.mutuo})

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
	desc_pg=request.GET.get("desc_pg")



	#limpiamos la tabla de pagos_temp para agregar los nuevos
	Pagos_Temp.objects.filter(usuario=usuario).delete()

	#obtenemos todos los pagos no pagados.
	pagos=Pagos.objects.filter(boleta=boleta,pagado="N")

	for p in pagos:
		
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
		npt.fecha_vencimiento_real=p.fecha_vencimiento_real


		npt.save()



	if int(importe_abono)>0:
		nuevo_mutuo=fn_simula_refrendo(importe_abono,usuario,boleta,0,desc_pg)



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



@api_view(["GET","PUT"])
def api_kiltajes(request):
	resp = []
	if request.method == "GET":
		try:
			id_kilataje = request.GET.get("id_kilataje")
			ob_kilataje = Costo_Kilataje.objects.get(id = id_kilataje)

			if ob_kilataje.tipo_kilataje == None:
				#si no tiene almacenado el tipo de kilataje le ponemos por default empeño
				ob_kilataje.tipo_kilataje = Tipo_Kilataje.objects.get(id = 2)
				ob_kilataje.save()

			resp.append({"estatus":"1","tipo_producto":ob_kilataje.tipo_producto.id,"desc_kilataje":ob_kilataje.kilataje,"avaluo":str(ob_kilataje.avaluo),"tipo_kilataje":ob_kilataje.tipo_kilataje.id})
		except Exception as e:
			print(e)
			resp.append({"estatus":"0","msj":"Error al consultar el kilataje"})
	if request.method == "PUT":
		try:
			id_kilataje = request.data["id_kilataje"]
			avaluo = decimal.Decimal(request.data["avaluo"])

			ob_kilataje = Costo_Kilataje.objects.get(id = id_kilataje)
			ob_kilataje.fn_actualiza_kilataje(avaluo)
			resp.append({"estatus":"1"})
		except Exception as e:
			print(e)
			resp.append({"estatus":"0"})

	return Response(json.dumps(resp))











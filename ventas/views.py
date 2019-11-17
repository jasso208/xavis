from django.shortcuts import render
from .models import Detalle_Venta,Direccion_Envio_Venta,Venta,Carrito_Compras
from inventario.models import Productos,Tallas,Img_Producto
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
import decimal
import datetime
from django.urls import reverse
from .forms import Busqueda_Venta_Form,Venta_Form
from django.http.response import HttpResponseRedirect
from seguridad.models import Direccion_Envio_Cliente_Temporal,Clientes_Logueados,Cliente
from django.core.mail import EmailMessage
from decimal import Decimal

def busca_ventas(request):
	if not request.user.is_authenticated:	
		return HttpResponseRedirect(reverse('seguridad:login'))

	if request.method=="POST":
		fecha_i=request.POST.get("fecha_inicial")
		fecha_f=request.POST.get("fecha_final")
		
		if request.POST.get("id_estatus_venta"):		
			id_estatus_venta=int(request.POST.get("id_estatus_venta"))
		else:			
			id_estatus_venta=0
			
		if fecha_i=="" and fecha_i=="" and id_estatus_venta==0:
			ventas=Venta.objects.all()
		if fecha_i!="" and fecha_i!="":
			if id_estatus_venta>0:
				ventas=Venta.objects.filter(fecha__range=(fecha_i,fecha_f),id_estatus_venta=id_estatus_venta)		
			else:
				ventas=Venta.objects.filter(fecha__range=(fecha_i,fecha_f))		
		if id_estatus_venta>0:
			if fecha_i!="" and fecha_i!="":
				ventas=Venta.objects.filter(fecha__range=(fecha_i,fecha_f),id_estatus_venta=id_estatus_venta)		
			else:
				ventas=Venta.objects.filter(id_estatus_venta=id_estatus_venta)
		form=Busqueda_Venta_Form(request.POST)
	else:
		form=Busqueda_Venta_Form()
		ventas=Venta.objects.all()
	return render(request,'ventas/busca_ventas.html',locals())

def detalle_venta_form(request,id_venta):	
	if not request.user.is_authenticated:	
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	venta=Venta.objects.get(id=id_venta)
	if request.method=="POST":
		form=Venta_Form(request.POST,instance=venta)	
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('ventas:busca_ventas'))
	else:
		det_venta=Detalle_Venta.objects.filter(id_venta=venta)
		direccion_enviio=Direccion_Envio_Venta.objects.get(id_venta=venta)
		form=Venta_Form(instance=venta)	
	return render(request,'ventas/ventas.html',locals())
	
#esta api, regresa los productos que estan en el carrito de compras de de la sessionq ue recibe como parametro
#tambien inserta productos al carrito de compras.
#parametros
#	Session
@api_view(['GET','POST'])
def api_consulta_carrito_compras(request):
	if request.method=="GET":
		carrito=[]
		session=request.GET.get("session")		
		#obtenemos los productos que estan en el carrito de compras.
		c_c=Carrito_Compras.objects.filter(session=session)

		if c_c.exists():
			
			for cc in c_c:
				try:
					ip=Img_Producto.objects.get(id_producto=cc.id_producto,orden=1)
					nom_img=ip.nom_img
				except:
					print("el producto no tiene imagen con valor 1 en el campo orden")
					nom_img=""				
				if cc.id_producto.descuento!=0:
					#obtenemos el precio sin iva
					sub_total=decimal.Decimal(cc.id_producto.precio)/decimal.Decimal(1.16)
					#obtenemos el subtotal con descuento
					sub_total_con_desc=decimal.Decimal(sub_total)-(decimal.Decimal(sub_total)*(decimal.Decimal(cc.id_producto.descuento/100.00)))
					#una vez que tenemos el precio con descuento, le agregamos el iva
					sub_total_con_iva=decimal.Decimal(sub_total_con_desc)*decimal.Decimal(1.16)
					precio_desc=sub_total_con_iva
				else:
					precio_desc=cc.id_producto.precio
				carrito.append({'marca':cc.id_producto.marca,'nombre':cc.id_producto.nombre,'id':cc.id,'id_producto':cc.id_producto.id,'precio':precio_desc,'id_producto':cc.id_producto.id,'nom_img':nom_img,'cantidad':cc.cantidad,'talla':cc.talla.talla})					
		return Response(carrito)
	if request.method=="POST":
		error=[]
		try:			
			#parametros
			id_producto=request.POST.get("id_producto")
			session=request.POST.get("session")
			cantidad=int(request.POST.get("cantidad"))
			id_talla=request.POST.get("id_talla")
			
			#parametros
			try:
				producto=Productos.objects.get(id=id_producto)
			except Exception as e:
				print(e)				
				error.append({'estatus':0,'msj':'El producto no existe.'})
				return Response(error)
			
			try:
				talla=Tallas.objects.get(id=id_talla)
			except Exception as e:
				print(e)
				error.append({'estatus':0,'msj':'Erro al encontrar la talla solicitada.'})				
				return Response(error)
			try:
				#en caso de que exista ya un registro en el carrito que cumpla con la session, producto y talla
				#envia error ya que todos los productos son pieza unica, y no puede agregar mas de uno.
				cc=Carrito_Compras.objects.get(session=session,id_producto=producto,talla=talla)				
				error.append({'estatus':0,'msj':'Este producto es pieza unica y ya lo tienes agregado a tu carrito.'})
				return Response(error)
				
				#cuando se tenga mas de una existencia de un mismo producto, habilitar las lineas de abajo.
				#cc.cantidad=int(cc.cantidad)+int(cantidad)
				#cc.save()
			except Exception as e:
				#en caso de que no existe el registro en el carrito que cumpla con la session, producto y talla
				#se crea uno nuevo.
				print(e)
				Carrito_Compras.objects.create(session=session,id_producto=producto,cantidad=cantidad,talla=talla)			
			error.append({'estatus':1,'msj':'El producto se agrego correctamente.'})
		except Exception as e:
			print(e)
			error.append({'estatus':0,'msj':'Error al agregar el producto, intente nuevamente.'})
		return Response(error)



#al parecer django no soporta el metodo delete, por lo tanto eliminar un producto del carrito
# se ara atravez de una url diferente por el metodo post
@api_view(['POST'])		
def api_elimina_carrito_compras(request):
	if request.method=="POST":
		error=[]
		try:			
			print(request.POST.get("id"))
			#parametros
			id_carrito=request.POST.get("id")			
			#parametros
			Carrito_Compras.objects.get(id=id_carrito).delete()
			error.append({"estatus":1,"msj":""})
		except Exception as e:
			print(e)
			error.append({"estatus":0,"msj":"Error al eliminar el producto del carrito, intente nuevamente."})
		return Response(error)



		
#guardamos la venta, almacenando la direccion de envio 
#parametros:
#	session:
#			Solo recibe este parametro ya que el resto de la informacion esta ya almacenada ligada a esta session.
@api_view(['POST'])		
def api_crea_venta(request):
	if request.method=="POST":
		folio_venta=[]
		session=request.POST.get("session")
		try:
			
			c_l=Clientes_Logueados.objects.get(session=session)
			cliente=c_l.cliente		
		except:
			#si no exite cliente logueado, valida el usuario que tiene el correo electronico dado,
			#si no existe cliente registrado, crea una cuenta para ese correo.			
			e_m=Direccion_Envio_Cliente_Temporal.objects.get(session=session)
			try:
				c_l=Cliente.objects.get(e_mail=e_m.e_mail.strip().upper())
				cliente=c_l		
			except Exception as e:
				print(e)
				Cliente.objects.create(e_mail=e_m.e_mail.strip().upper())
				c_l=Cliente.objects.get(e_mail=e_m.e_mail.strip().upper())
				cliente=c_l		
		#obtenemos la inormacion guardada en la session
		c_c=Carrito_Compras.objects.filter(session=session)
		if c_c.exists():
			try:
				d_e=Direccion_Envio_Cliente_Temporal.objects.get(session=session)		
			except:
				#sillega a la except es porque no tiene capturada la direccion de envio
				folio_venta.append({"estatus":0,"msj":"No se ha agregado la direccion de envio."})			
				return Response(folio_venta)			
			#calculamos el total de la venta
			total=0.00
			descuento=0.00
			iva=0.00
			for cc in c_c:					
				#calculamos el precio de venta(en caso de tener descuento)					
				if cc.id_producto.descuento!=0:
					#obtenemos el precio sin iva
					sub_total=decimal.Decimal(cc.id_producto.precio)/decimal.Decimal(1.16)
					#obtenemos el descuento
					descuento=decimal.Decimal(descuento)+(decimal.Decimal(sub_total)*(decimal.Decimal(cc.id_producto.descuento/100.00)))
					descuento=decimal.Decimal(descuento)*decimal.Decimal(cc.cantidad)								
					#obtenemos el subtotal con descuento
					sub_total_con_desc=decimal.Decimal(sub_total)-(decimal.Decimal(sub_total)*(decimal.Decimal(cc.id_producto.descuento/100.00)))
					#una vez que tenemos el precio con descuento, le agregamos el iva y lo multiplicamos por la cantidad
					sub_total_con_iva=(decimal.Decimal(sub_total_con_desc)*decimal.Decimal(1.16))*decimal.Decimal(cc.cantidad)								
				else:
					sub_total_con_iva=decimal.Decimal(cc.id_producto.precio)*decimal.Decimal(cc.cantidad)				
				#total ya con iva
				total=decimal.Decimal(total)+decimal.Decimal(sub_total_con_iva)
				#el subtotal es sin iva
				sub_total=decimal.Decimal(decimal.Decimal(total)/decimal.Decimal(1.16))+decimal.Decimal(descuento)
				#el iva es la diferencia entre el total y el subtotal
				#iva=decimal.Decimal(sub_total)*decimal.Decimal(0.16)
			#CREAMOS LA VENTA
			iva=decimal.Decimal(decimal.Decimal(sub_total)-decimal.Decimal(descuento))*decimal.Decimal(0.16)
			v=Venta(total=total,sub_total=sub_total,iva=iva,descuento=descuento,cliente=cliente)
			v.save()
			
			#recorremos los productos del carrito para crear el detalle d ela venta
			for cc in c_c:
				#calculamos el precio de venta(en caso de tener descuento)	
				precio_unitario=0.00
				descuento=0.00
				iva=0.00
				precio_total=0.00
				if cc.id_producto.descuento!=0:
					precio_unitario=decimal.Decimal(cc.id_producto.precio)/decimal.Decimal(1.16)#precio antes de iva
					descuento=decimal.Decimal(precio_unitario)*(decimal.Decimal(cc.id_producto.descuento)/decimal.Decimal(100))
					iva=(decimal.Decimal(precio_unitario)-decimal.Decimal(descuento))*decimal.Decimal(0.16)
					precio_total=(decimal.Decimal(precio_unitario)-decimal.Decimal(descuento)+decimal.Decimal(iva))*decimal.Decimal(cc.cantidad)
				else:
					precio_unitario=decimal.Decimal(cc.id_producto.precio)/decimal.Decimal(1.16)
					iva=decimal.Decimal(precio_unitario)*decimal.Decimal(0.16)
					precio_total=decimal.Decimal(cc.id_producto.precio)*decimal.Decimal(cc.cantidad)
				#guardamos el detalle de la venta
				d=Detalle_Venta(id_venta=v,id_producto=cc.id_producto,cantidad=cc.cantidad,talla=cc.talla,precio_unitario=precio_unitario,descuento=descuento,iva=iva,precio_total=precio_total)				
				d.save()
			#agregamos la direccion de envio a la venta.
			dir_envio=Direccion_Envio_Venta(id_venta=v,nombre_recibe=d_e.nombre,apellido_p=d_e.apellido_p,apellido_m=d_e.apellido_m,calle=d_e.calle,numero_interior=d_e.numero_interior,numero_exterior=d_e.numero_exterior,cp=d_e.cp,municipio=d_e.municipio,estado=d_e.estado,pais=d_e.pais,telefono=d_e.telefono,correo_electronico=d_e.e_mail,referencia=d_e.referencia)
			dir_envio.save()
			#borramos la informacion de la session del cliente
			c_c.delete()
			d_e.delete()
			folio_venta.append({"estatus":1,"folio":str(v.id)})							
		else:
			folio_venta.append({"estatus":0,"msj":"No tiene productos agregados al carrito de compras."})
		return Response(folio_venta)


#obtenemos la cantidad de productos que estan en carrito de compras.
#parametros:
#	session
@api_view(['GET'])
def api_cont_productos_carrito(request):		
	if request.method=="GET":	
	#	print("entro a enviar correo")
	#	email = EmailMessage('title', 'body', to=['jasso.gallegos@gmail.com'])
	#	email.send()			
		contador=[]		
		session=request.GET.get("session")				
		#obtenemos los productos que estan en el carrito de compras.
		c_c=Carrito_Compras.objects.filter(session=session).aggregate(Sum('cantidad'))
		print(c_c)		
		contador.append(c_c)		
		
		return Response(contador)
		

#obtenemos el listado de ventas del cliente logueado.
@api_view(['GET'])
def api_consulta_ventas(request):
	respuesta=[]
	try:
		session=request.GET.get("session")
		c_l=Clientes_Logueados.objects.get(session=session)
		cliente=c_l.cliente
		ventas=Venta.objects.filter(cliente=cliente).order_by('-fecha')
		for v in ventas:			
			respuesta.append({"estatus":"1","msj":"","id_venta":v.id,"descuento":v.descuento,"fecha":v.fecha,"sub_total":v.sub_total,"iva":v.iva,"total":v.total,"link_seg":v.link_seguimiento})
	except Exception as e:
		print(e)
		respuesta.append({"estatus":"0","msj":"Error al consultar las ventas, intente refrescar la pagina."})
	return Response(respuesta)

@api_view(['GET'])	
def api_consulta_detalle_venta(request):
	respuesta=[]
	try:
		id_venta=request.GET.get("id_venta")
		venta=Venta.objects.get(id=id_venta)
		print(venta)
		d_v=Detalle_Venta.objects.filter(id_venta=venta)
		
		for v in d_v:
			try:
				ip=Img_Producto.objects.get(id_producto=v.id_producto,orden=1)
				nom_img=ip.nom_img
			except Exception as e:
				print(e)
				nom_img=""				
			respuesta.append({"estatus":"1","msj":"","nom_img":nom_img,'nombre':v.id_producto.nombre,"cantidad":v.cantidad,"talla":v.talla.talla,"precio_unitario":Decimal(v.precio_unitario)*Decimal(1.16),"marca":v.id_producto.marca})
	except Exception as e:
		print(e)
		respuesta.append({"estatus":"0","msj":"Error al consultar el detalle de la venta."})
	return Response(respuesta)
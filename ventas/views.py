from django.shortcuts import render
from .models import Detalle_Venta,Direccion_Envio_Venta,Venta,Carrito_Compras
from inventario.models import Productos,Tallas,Img_Producto
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
import decimal
import datetime
from django.urls import reverse
from .forms import Busqueda_Venta_Form,Venta_Form,Medio_Venta_Form,Det_Venta_Form
from django.http.response import HttpResponseRedirect
from seguridad.models import Direccion_Envio_Cliente_Temporal,Clientes_Logueados,Cliente
from django.forms.models import inlineformset_factory
from decimal import Decimal
from contabilidad.models import Concepto_Gasto,Concepto_Ingreso,Movs_Gasto,Movs_Ingreso
import openpay
import smtplib
import email.message
from smart_selects.db_fields import ChainedForeignKey
from django.forms import widgets
openpay.api_key = "sk_f0e4778198cb46a69fd64b50d1276efa"
openpay.verify_ssl_certs = False
openpay.merchant_id = "myllylbt6vwlywximkxg"
openpay.production = False  # By default this works in sandbox mode


encabezado_0="""
<html>
    <head>           
    </head>
    <body style="background-color:#e9e9e9;">
        <table style="width: 300px;; margin:0 auto;background-color: white;"  cellpadding="10" cellspacing="0">
            <tr style="background-color: black;">
                <td colspan="2">
                        <img src="http://jasso208.pythonanywhere.com/assets/img/logo_peque.png" style="width: 50px;">
                </td>
                <td colspan="4" style="text-align: right;" valign="bottom">
                   
                    <p style="color: white;font-family: sans-serif;">Folio Compra: 
"""
encabezado_1="""					
					</p>
                </td>
            </tr>
            <tr>
                <td colspan="6">
                    <img src="http://jasso208.pythonanywhere.com/assets/img/img-gracias.png" width="300px;">
                </td>
            </tr>
            <tr>
                <td colspan="6">
                    <hr>
                </td>
            </tr>
            <tr>
                <td colspan="6">
                    <p style="font-family: sans-serif">
                      
                            Resumen de Compra
                        
                    </p>
                </td>
            </tr>
            
            <tr>
                    <td colspan="6">
                        <hr>
                    </td>
                </tr>
            <tr>
                <td colspan="6">
                    <p style="font-family: sans-serif ;font-size: 12px;">
                        
                            Detalle de envio
                        
                    </p>
                    <p style="color: gray;font-size: 12;font-family: sans-serif;">
"""

encabezado_2="""
                    </p>
                    <p style="font-family: sans-serif ;font-size: 12px;">
                        
                            Recibe:
                        
                    </p>
                    <p style="color: gray;font-size: 12;font-family: sans-serif;">
"""
                            
encabezado_3="""
                        </p>

                </td>
            </tr>
            <tr>
                    <td colspan="6">
                        <hr>
                    </td>
                </tr>
            <tr>
                <td colspan="6">
                        <p style="font-family: sans-serif ;font-size: 12px;">
                        
                               Productos
                            
                        </p>
                </td>
            </tr>
            
"""
encabezado_4="""   
           
            <tr>
                <td colspan="6">
                    <hr>
                </td>
            </tr>
            <tr>
                <td colspan="6">
                    <p style="font-family: sans-serif ;font-size: 12px;">
                        Pagaste
                    </p>
                </td>
            </tr>
            <tr>
                <td colspan="4">
                    <p style="font-family: sans-serif ;font-size: 12px;text-align: right;">
                        Sub Total
                    </p>
                </td>
                
                <td colspan="2">
                        <p style="font-family: sans-serif ;font-size: 12px;text-align: right;">
			
                            $
							"""
encabezado_5="""
				
                        </p>
                    </td>
            </tr>
            <tr>
                    <td colspan="4">
                        <p style="font-family: sans-serif ;font-size: 12px;text-align: right;">
                           Costo de Envio
                        </p>
                    </td>
                    
                    <td colspan="2">
                            <p style="font-family: sans-serif ;font-size: 12px;text-align: right;">
                                $
"""
encabezado_6="""

                            </p>
                        </td>
                </tr>
                <tr>
                    <td colspan="4">
                        <p style="font-family: sans-serif ;font-size: 12px;text-align: right;">
                            Total
                        </p>
                    </td>
                    
                    <td colspan="2">
                            <p style="font-family: sans-serif ;font-size: 12px;text-align: right;">
                                $
								"""
encabezado_7="""
								
                            </p>
                        </td>
                </tr>
                <tr>
                        <td colspan="6">
                            <hr>
                        </td>
                    </tr>
        </table>
    </body>
</html>
"""


#registramos el medio de venta, mercado libre, facebook, instagram etc
def registro_medio_venta(request):
	if not request.user.is_authenticated:	
		return HttpResponseRedirect(reverse('seguridad:login'))
	if request.method=="POST":
		form=Medio_Venta_Form(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('seguridad:bienvenidos'))
	else:
		form=Medio_Venta_Form()
	return render(request,"ventas/medio_venta.html",locals())

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

#cuando se crea una vent desde mercado libre o facebook o algun otro canal, se registra la venta por esta vista
def guarda_venta_manual(request,id_venta=None):
	if not request.user.is_authenticated:	
		return HttpResponseRedirect(reverse('seguridad:login'))	

	if id_venta:
		venta=Venta.objects.get(id=id_venta)
	else:
		venta=Venta()

	#creamos formset del detalle de la venta
	Detalle_Venta_Formset=inlineformset_factory(Venta,Detalle_Venta,form=Det_Venta_Form,extra=1,can_delete=True)

	if request.method=="POST":
		
		form=Venta_Form(request.POST,instance=venta)
		detalle_venta_formset=Detalle_Venta_Formset(request.POST, instance=venta)
	
	
		if form.is_valid() and detalle_venta_formset.is_valid():
			form.save()
			detalle_venta_formset.save()
			Direccion_Envio_Venta.objects.create(id_venta=venta,nombre_recibe='NA',apellido_p="NA",apellido_m="NA",calle="NA",numero_interior="NA",numero_exterior="NA",cp="NA",colonia="NA",municipio="NA",estado="NA",pais="NA",telefono="NA",correo_electronico="NA",referencia="NA")
			Detalle_Venta.objects.filter(id_venta=venta,cantidad=0).delete()

			#obtenemos el concepto para ingreso por venta.
			ci=Concepto_Ingreso.objects.get(id=1)
			Movs_Ingreso.objects.create(id_concepto_ingreso=ci,descripcion="Ingreso por Venta",importe=venta.total,id_v=venta,fecha=venta.fecha)

			return HttpResponseRedirect(reverse('ventas:busca_ventas'))
		else:			
			print(form.errors)
			print(detalle_venta_formset.errors)
	else:
		form=Venta_Form(instance=venta)
		detalle_venta_formset=Detalle_Venta_Formset(instance=venta)
	return render(request,'ventas/registra_venta.html',locals())

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


#generamos el cargo al cliente.
@api_view(['POST'])
def api_genera_cargo(request):
	estatus=[]
	try:
		charge = openpay.Charge.create_as_merchant(
			method="card",
			amount=request.POST.get("amount"),
			description="Testing card charges from python",
			order_id="123123123",
			device_session_id=request.POST.get("deviceIdHiddenFieldName"),
			source_id=request.POST.get("token_id")  ,
			customer={
				"name":"Heber",
				"last_name":"Robles",
				"email":"xxxxx@example.com",
				"phone_number":"4429938834",
				"address":{
					"city": "Queretaro",
					"state":"Queretaro",
					"line1":"Calle de las penas no 10",
					"postal_code":"76000",
					"line2":"col. san pablo",
					"line3":"entre la calle de la alegria y la calle del llanto",
					"country_code":"MX"
				}
			},
			metadata={
				"data1":"value1",
				"data2":"value2"
			}
		)
		print(charge)
	except Exception as e:
		print("error")
		print(e)
	return Response(estatus)
	
		
#guardamos la venta, almacenando la direccion de envio 
#parametros:
#	session:
#			Solo recibe este parametro ya que el resto de la informacion esta ya almacenada ligada a esta session.
@api_view(['POST','GET'])		
def api_crea_venta(request):
	if request.method=="POST":
		session=request.POST.get("session")
		amount=request.POST.get("amount")
		description=request.POST.get("description")
		device_session_id=request.POST.get("deviceIdHiddenFieldName")
		source_id=request.POST.get("token_id") 
	if request.method=="GET":
		session=request.GET.get("session")
		amount=request.GET.get("amount")
		description=request.GET.get("description")
		device_session_id=request.GET.get("deviceIdHiddenFieldName")
		source_id=request.GET.get("token_id") 
	print(session)
	folio_venta=[]		
	try:
		c_l=Clientes_Logueados.objects.get(session=session)
		cliente=c_l.cliente		
	except:
		#si no exite cliente logueado, valida el usuario que tiene el correo electronico dado,
		#si no existe cliente registrado, crea una cuenta para ese correo.	1			
		try:
			e_m=Direccion_Envio_Cliente_Temporal.objects.get(session=session)
		except:
			#sillega a la except es porque no tiene capturada la direccion de envio
			folio_venta.append({"estatus":0,"msj":"No se ha agregado la direccion de envio."})			
			return Response(folio_venta)
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
		dir_envio=Direccion_Envio_Venta(id_venta=v,nombre_recibe=d_e.nombre,colonia=d_e.colonia,apellido_p=d_e.apellido_p,apellido_m=d_e.apellido_m,calle=d_e.calle,numero_interior=d_e.numero_interior,numero_exterior=d_e.numero_exterior,cp=d_e.cp,municipio=d_e.municipio,estado=d_e.estado,pais=d_e.pais,telefono=d_e.telefono,correo_electronico=d_e.e_mail,referencia=d_e.referencia)
		dir_envio.save()
		#generamos el cargo 
		try:
			charge = openpay.Charge.create_as_merchant(
				method="card",
				amount=amount,
				description=description,
				order_id=str(v.id),
				device_session_id=device_session_id,
				source_id=source_id,
				customer={
					"name":d_e.nombre,
					"last_name":d_e.apellido_p,
					"email":d_e.e_mail,
					"phone_number":d_e.telefono,
					"address":{
						"city": d_e.municipio,
						"state":d_e.estado,
						"line1":d_e.calle,
						"postal_code":d_e.cp,
						"line2":d_e.colonia,
						"line3":d_e.referencia,
						"country_code":"MX"
					}
				},
				metadata={
					"data1":"value1",
					"data2":"value2"
				}
			)
			#si se genero correctamente el cargo a la tarjeta
			#borramos la informacion de la session del cliente
			c_c.delete()
			d_e.delete()
			folio_venta.append({"estatus":1,"folio":str(v.id)})	
			#notificamos a el vendeor que uvo una venta
			fn_envia_email(v)				
		except Exception as e:
			#borramos los registros de la venta, ya que el pago no pudo realizarse
			Detalle_Venta.objects.filter(id_venta=v).delete()
			Direccion_Envio_Venta.objects.filter(id_venta=v).delete()					
			v.delete()
			folio_venta.append({"estatus":0,"msj":"Su banco no puede procesar el pago."})									
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


def reenvia_venta(request,id_venta):	
	if not request.user.is_authenticated:	
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	v=Venta.objects.get(id=id_venta)
	
	if request.method=="POST":
		fn_envia_email(v)
	else:
		fn_envia_email(v)
	return render(request,'ventas/busca_ventas.html',locals())


#funcion para enviar corre de confirmacion de compra
def fn_envia_email(v):
	global encabezado_1,encabezado_2
	try:
		d_e=Direccion_Envio_Venta.objects.get(id_venta=v)
		direccion_envio=d_e.calle+" Num."+d_e.numero_exterior+", "+d_e.colonia+" "+d_e.municipio+", "+d_e.estado+" "+d_e.pais+"<br>Referencia Domicilio: "+d_e.referencia
		nom_recibe=d_e.nombre_recibe+" "+d_e.apellido_p+" "+d_e.apellido_m
		productos=""
		d_v=Detalle_Venta.objects.filter(id_venta=v)
		subtotal=decimal.Decimal('0.0')
		for p in d_v:			
			subtotal=subtotal+(p.precio_unitario*decimal.Decimal('1.16'))
			cad="<tr><td colspan='1'><img src='http://jasso208.pythonanywhere.com/assets/img/productos/"+fn_concatena_folio(str(p.id_producto.id))+"_1.png' style='width: 100px;'></td><td colspan='3'><p style='color: gray;font-size: 12;font-family: sans-serif;'>"+p.id_producto.nombre+"</p></td><td colspan='3'><p style='color: gray;font-size: 12;font-family: sans-serif;'>$"+str(round(p.precio_unitario*decimal.Decimal('1.16'),2))+"</p></td></tr>"
			productos=productos+cad
		subtotal=round(subtotal,2)
		costo_envio=decimal.Decimal('0.0')
		if v.total<decimal.Decimal('800.0'):
			costo_envio=decimal.Decimal('100.0')

		html=encabezado_0+fn_concatena_folio(str(v.id))+encabezado_1+direccion_envio+encabezado_2+nom_recibe+encabezado_3+productos+encabezado_4+str(subtotal)+encabezado_5+str(costo_envio)+encabezado_6+str(v.total+costo_envio)+encabezado_7
		html = html.replace("\xe9", "e")
		html = html.replace("\x0a", "\n")
		server = smtplib.SMTP('smtp.gmail.com:587')
		msg = email.message.Message()
		msg['Subject'] = 'Confirmacion de Compra'		
		
		msg['From'] = 'j.jassdel@gmail.com'
		msg['To'] = v.cliente.e_mail
		password = "JaSSDEL1985"
		msg.add_header('Content-Type', 'text/html')
		msg.set_payload(html)		
		s = smtplib.SMTP('smtp.gmail.com: 587')
		s.starttls()		
		# Login Credentials for sending the mail
		s.login(msg['From'], password)		
		s.sendmail(msg['From'], [msg['To']], msg.as_string())
		#email = EmailMessage('Venta Registrada', 'ID de la venta: '+str(v.id), to=["gerencia.jassdel@jassdel.com"])
		#email.send()
		return 1#se ejecuto con exito
	except Exception as e:
		server = smtplib.SMTP('smtp.gmail.com:587')
		msg = email.message.Message()
		msg['Subject'] = 'Error al notificar al cliente su compra'		
		html="Error al notifica al cliente la compra con folio: "+str(v.id)+"; "+str(e)
		msg['From'] = 'j.jassdel@gmail.com'
		msg['To'] = 'gerencia.jassdel@jassdel.com'
		password = "JaSSDEL1985"
		msg.add_header('Content-Type', 'text/html')
		msg.set_payload(html)		
		s = smtplib.SMTP('smtp.gmail.com: 587')
		s.starttls()		
		# Login Credentials for sending the mail
		s.login(msg['From'], password)		
		s.sendmail(msg['From'], [msg['To']], msg.as_string())	
		return 0#fallo la ejecucion

def fn_concatena_folio(folio):
	f=""
	if len(folio)==7:
		f=folio
	if len(folio)==6:
		f="0"+folio
	if len(folio)==5:
		f="00"+folio
	if len(folio)==4:
		f="000"+folio
	if len(folio)==3:
		f="0000"+folio
	if len(folio)==2:
		f="00000"+folio
	if len(folio)==1:
		f="000000"+folio
	return f

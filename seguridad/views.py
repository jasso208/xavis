from django.views.generic.edit import FormView
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth import logout
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from seguridad.models import Cliente,Direccion_Envio_Cliente,Clientes_Logueados,Direccion_Envio_Cliente_Temporal
from seguridad.models import E_Mail_Notificacion,Recupera_pws
from django.core.mail import EmailMessage
from ventas.models import Venta,Detalle_Venta

import smtplib
import email.message

encabezado_link_consulta_venta_1="""
<html>
    <head>           
    </head>
    <body style="background-color:#e9e9e9;">
        <table style="width: 300px;; margin:0 auto;background-color: white;"  cellpadding="10" cellspacing="0">
            <tr style="background-color: black;">
                <td colspan="6">
                        <img src="https://www.jassdel.com/assets/img/logo_peque.png" style="width: 50px;">
                </td>
            </tr>
			<tr>
				<td colspan="6">
					<p>Hola:<br><br><br>
					&nbsp;&nbsp;&nbsp; De click en el siguiente vinculo para poder consultar sus ventas:
					<br><br>
					
					</p>
					<a href="
"""
					
encabezado_link_consulta_venta_2="""
					">Click para consultar Ventas</a>
					<br><br>
					<p>Saludos.</p>				
				</td>
			</tr>
		</table>
	</body>
</html>
"""


class Login(FormView):
	template_name="login.html"
	form_class=AuthenticationForm
	success_url="/bienvenidos"
	def dispatch(self,request,*args,**kwargs):
		if request.user.is_authenticated:
			return HttpResponseRedirect("/bienvenidos")
		else:
			return super(Login,self).dispatch(request,*args,**kwargs)
	def form_valid(self,form):
		login(self.request,form.get_user())
		return super(Login,self).form_valid(form)

def bienvenidos(request):
	return render(request,'seguridad/bienvenidos.html',{})

#esta api recibe la session y la desvincula de la cuenta logueada,
#esto con la finalidad de no perder los carritos agregados al carrito de compras.
@api_view(['POST'])
def api_kill_session(request):
	error=[]
	if request.method=="POST":
		session=request.POST.get("session")
		Clientes_Logueados.objects.get(session=session).delete()
	return Response(error)

#api para crear cuentas de clientes
#en caso de ya existir, actualiza la cuenta.
#	En caso de que se reciba la session, es porque se trata de un actualizacion a un cliente
#	En caso de que no se reciba la session, es porque es un cliente nuevo.
@api_view(['POST'])
def api_alta_cliente(request):
	estatus=[]
	if request.method=="POST":		
		try:			
			session=request.POST.get("session")
			if session==None:
				session=""				
			#print(request.POST.get("e_mail"))
			nombre=request.POST.get("nombre")
			apellido_p=request.POST.get("apellido_p")
			apellido_m=request.POST.get("apellido_m")
			telefono=request.POST.get("telefono")				
			e_mail=request.POST.get("e_mail").upper()
			rfc=request.POST.get("rfc")
			psw=request.POST.get("psw")
		
			numero_interior=request.POST.get("numero_interior")
			numero_exterior=request.POST.get("numero_exterior")
			calle=request.POST.get("calle_reg")
			cp=request.POST.get("cp")
			municipio=request.POST.get("municipio")
			estado=request.POST.get("estado")
			#pais=request.POST.get("pais")		
			referencia=request.POST.get("referencia")
			
			#obtenemos el cliente logueado con la session.
			try:#si existe cliente logueado lo actualizamos
				c_l=Clientes_Logueados.objects.get(session=session)
				c=Cliente.objects.get(id=c_l.cliente.id)
				
				#c.psw=psw
				c.nombre=nombre
				c.apellido_p=apellido_p
				c.apellido_m=apellido_m
				c.telefono=telefono
				#c.e_mail=e_mail
				c.rfc=rfc
				c.save()
				
				try:					
					d_e=Direccion_Envio_Cliente.objects.get(cliente=c)					
					d_e.numero_interior=numero_interior
					d_e.numero_exterior=numero_exterior
					d_e.calle=calle
					d_e.cp=cp
					d_e.municipio=municipio
					d_e.estado=estado
					d_e.pais="Mexico"
					d_e.referencia=referencia
					d_e.save()
				except:
					d_e=Direccion_Envio_Cliente(cliente=c,numero_interior=numero_interior,numero_exterior=numero_exterior,calle=calle,cp=cp,municipio=municipio,estado=estado,pais=pais,referencia=referencia)
					
					d_e.save()
					print(d_e.numero_interior)
			except Exception as e:#de lo contrario creamos registro
				#validamos si existe el e mail
				c=Cliente.objects.filter(e_mail=e_mail).exists()
				if c:
					estatus.append({"estatus":"0","msj":"Ya existe una cuenta con este e_mail."})
					return Response(estatus)	
				else:
					c=Cliente(psw=psw,nombre=nombre,apellido_p=apellido_p,apellido_m=apellido_m,telefono=telefono,e_mail=e_mail.upper(),rfc=rfc)
					c.save()			
					d_e=Direccion_Envio_Cliente(cliente=c,numero_interior=numero_interior,numero_exterior=numero_exterior,calle=calle,cp=cp,municipio=municipio,estado=estado,pais="Mexico",referencia=referencia)
					d_e.save()			
			#el estatus 1 indica que se guardo correctamente el cliente.
			estatus.append({"estatus":"1","msj":""})
		except Exception as e:
			print(e)
			#el estatus cero indica que fallo
			estatus.append({"estatus":"0","msj":""})
	return Response(estatus)	

	
#api para identificar al usuario
@api_view(["POST"])
def api_login_usuario(request):
	cliente=[]	
	e_mail=request.POST.get("e_mail").upper()
	psw=request.POST.get("psw")
	session=request.POST.get("session")	
	print(e_mail)
	print(psw)
	print(session)
	try:
		c=Cliente.objects.get(e_mail=e_mail,psw=psw)
	except Exception as e:
		cliente.append({"estatus":"0","msj":"El e_mail/contraseña es incorrecta."})
		print(e)
		return Response(cliente)
	try:
		#si encuentra informacion, es porque ya hay un cliente logueado.
		c_l=Clientes_Logueados.objects.get(cliente=c,session=session)
		cliente.append({"estatus":"0","msj":"Ya has iniciado session. Da click en el boton salir para inciar con otra cuenta."})
		return Response(cliente)
	except Exception as w:
		print(w)			
	try:
		Clientes_Logueados.objects.create(cliente=c,session=session)
		cliente.append({"estatus":"1","msj":"Exito","nombre":c.nombre,"apellido_p":c.apellido_p,"apellido_m":c.apellido_m})		
		de=Direccion_Envio_Cliente.objects.get(cliente=c)
		#en caso de existir ya una direccion temporal registrada, la eliminamos y cargamos
		#la infoamcion que tiene registrada en la cuenta.
		Direccion_Envio_Cliente_Temporal.objects.filter(session=session).delete()
		#Insertamos la informacion de la cuenta del cliente, para que sea mostrada por default al momento de terminar la venta,
		#esta infmormacion podra ser modificada por el cliente.		
		Direccion_Envio_Cliente_Temporal.objects.create(session=session,nombre=c.nombre,apellido_p=c.apellido_p,apellido_m=c.apellido_m,telefono=c.telefono,e_mail=c.e_mail,rfc=c.rfc,calle=de.calle,numero_interior=de.numero_interior,numero_exterior=de.numero_exterior,cp=de.cp,municipio=de.municipio,estado=de.estado,pais=de.pais,	referencia=de.referencia)
		
		return Response(cliente)
	except Exception as e:
		cliente.append({"estatus":"0","msj":"El e_mail/contraseña es incorrecta."})
		print(e)
	return Response(cliente)
	
#api par identificar si un usuario ya esta logueado
@api_view(["GET"])
def api_esta_logueado(request):
	estatus=[]
	session=request.GET.get("session")	
	print(session)
	try:
		c_l=Clientes_Logueados.objects.get(session=session)
		try:
			dir=Direccion_Envio_Cliente.objects.get(cliente=c_l.cliente)		
		except:
			print("El cliente no tiene direccion de envio registrada")
			estatus.append({"estatus":"1","nombre":c_l.cliente.nombre,"apellido_p":c_l.cliente.apellido_p,"apellido_m":c_l.cliente.apellido_m})		
		estatus.append({"rfc":c_l.cliente.rfc,"e_mail":c_l.cliente.e_mail.upper(),"telefono":c_l.cliente.telefono,"estatus":"1","nombre":c_l.cliente.nombre,"apellido_p":c_l.cliente.apellido_p,"apellido_m":c_l.cliente.apellido_m,"calle":dir.calle,"numero_interior":dir.numero_interior,"numero_exterior":dir.numero_exterior,"cp":dir.cp,"municipio":dir.municipio,"estado":dir.estado,"pais":dir.pais,"referencia":dir.referencia})		
	except Exception as e:
		#no se pudo identificar si el cliente ya eta logueado
		estatus.append({"estatus":"0"})
		print(e)
	return Response(estatus)
	
#api para establecer/obtener la direccion de ennvio de una session
#solo para usuarios no logueados.
@api_view(['POST','GET'])
def api_direccion_envio_temporal(request):
	estatus=[]
	try:
		if request.method=="POST":
			print(request.POST.get("colonia"))
			session=request.POST.get("session")	
			nombre=request.POST.get("nombre")
			apellido_p=request.POST.get("apellido_p")
			apellido_m=request.POST.get("apellido_m")
			telefono=request.POST.get("telefono")				
			e_mail=request.POST.get("e_mail").upper()
			rfc=request.POST.get("rfc")	
			numero_interior=request.POST.get("numero_interior")
			numero_exterior=request.POST.get("numero_exterior")
			calle=request.POST.get("calle")
			cp=request.POST.get("cp")
			municipio=request.POST.get("municipio")
			estado=request.POST.get("estado")
			pais=request.POST.get("pais")		
			referencia=request.POST.get("referencia")				
			colonia=request.POST.get("colonia")		
			#borramos la direccion de envio que ya tiene esa session
			Direccion_Envio_Cliente_Temporal.objects.filter(session=session).delete()
			#insertamos la direccion de envio vinculanda a la session
			Direccion_Envio_Cliente_Temporal.objects.create(colonia=colonia,session=session,nombre=nombre,apellido_p=apellido_p,apellido_m=apellido_m,telefono=telefono,e_mail=e_mail,rfc=rfc,numero_interior=numero_interior,numero_exterior=numero_exterior,calle=calle,cp=cp,municipio=municipio,estado=estado,pais=pais,referencia=referencia)
			estatus.append({"estatus":"1","msj":"Se guardo correctamente la direccion."})
		if request.method=="GET":
			session=request.GET.get("session")				
			d=Direccion_Envio_Cliente_Temporal.objects.get(session=session)			
			estatus.append({"estatus":"1","msj":"Se guardo correctamente la direccion.","colonia":d.colonia,"nombre":d.nombre,"apellido_p":d.apellido_p,"apellido_m":d.apellido_m,"telefono":d.telefono,"e_mail":d.e_mail,"rfc":d.rfc,"numero_interior":d.numero_interior,"numero_exterior":d.numero_exterior,"calle":d.calle,"cp":d.cp,"municipio":d.municipio,"estado":d.estado,"pais":d.pais,"referencia":d.referencia})
	except Exception as e:	
		print(e)
		estatus.append({"estatus":"0","msj":"Error al guardar la direccion de envio,intente nuevamente."})
	return Response(estatus)
			
@api_view(['POST'])
def api_e_mail_notificacion(request):
	estatus=[]
	try:
		e_mail=request.POST.get("e_mail").upper()
		print(e_mail)
		try:			
			E_Mail_Notificacion.objects.get(e_mail=e_mail)
			estatus.append({"estatus":"1","msj":"El E-Mail ya ha sido registrado."})
		except Exception as e:
			E_Mail_Notificacion.objects.create(e_mail=e_mail)
			estatus.append({"estatus":"1","msj":"Te Subscribiste Corecctamente."})
		email = EmailMessage('Subscripcion Jassdel', 'Gracias por subscribirte%sA partir de este momento recibiras notificaciones de todas nuestras novedades.%sAtte: Equipo Jassdel.', to=[e_mail])
		email.send()	
	except Exception as e:		
		print(e)
		estatus.append({"estatus":"0","msj":"Ocurrio un Error al Subcribirte, Intentalo Nueva mente."})
	return Response(estatus)
	
#esta api actualiza la contraseña, del cliente
#	parametros
#		session: recibe la session para obtener el correo del cliente que intenta cambiar contraseña
#		contraseña actual: se recibe la contraseña actual para validar que otra persona no pueda cambiar la contraseña
#		contraseña nueva: es la nueva contraseña
@api_view(['POST'])
def api_actualiza_contrasena(request):
	estatus=[]
	try:
		if request.method=="POST":

			session=request.POST.get("session")
			psw_actual=request.POST.get("psw_actual")
			psw_nueva=request.POST.get("psw_nueva")

			#buscamos el cliente
			cliente=Clientes_Logueados.objects.get(session=session)

			#validamos que se identifique correctamente
			if cliente.cliente.psw==psw_actual:
				#guardamos la nueva contraseña
				cliente.cliente.psw=psw_nueva				
				cliente.cliente.save()
				estatus.append({"estatus":"1","msj":"Se actualizo correctamente la contraseña"})	
			else:
				estatus.append({"estatus":"0","msj":"La contraseña actual no es correcta"})	
		else:
			estatus.append({"estatus":"0","msj":"Error al actualizar tu contraseña 2."})	

	except Exception as e:
		print(e)
		estatus.append({"estatus":"0","msj":"Error al actualizar tu contraseña."})
	return Response(estatus)

#en esta api se llena la tabla creando la relacion del token con el email del que se desea recuperar la contraseña,
#para posteriormente enviar el correo con el link para actualizar la contraseña.
#parametros
#		token: es el token unico que nos ayudara a crear el link para cambiar contraseña,
#				este token se liga al correo
#		e_mail:	Es el email de la cuenta que se desea cambiar contraseña.
@api_view(['POST'])
def api_envia_token(request):
	estatus=[]
	try:
		e_mail=request.POST.get("e_mail").upper()
		session=request.POST.get("session")
		
		try:#validamos que exista el email en nuestrs cuentas
			Cliente.objects.get(e_mail=e_mail)
			
		except Exception as e:
			print(e)
			#si llega aqui es porque el e_mail no existe.
			estatus.append({"estatus":0,"msj":"El E-Mail no existe en la base de datos."})
			return Response(estatus)
		try:
			#borramos todas los registros de el email recibido
			Recupera_pws.objects.filter(e_mail=e_mail).delete()
			#borramos todas los registros de la session recibida
			Recupera_pws.objects.filter(session=session).delete()
			Recupera_pws.objects.create(session=session,e_mail=e_mail)
			ff=Recupera_pws.objects.get(session=session)
		except Exception as e:
			print(e)
		link="http://localhost:4200/#/listado_ventas/"+session
		html=encabezado_link_consulta_venta_1+link+encabezado_link_consulta_venta_2
		html = html.replace("\xe9", "e")
		html = html.replace("\x0a", "\n")
		server = smtplib.SMTP('smtp.gmail.com:587')
		msg = email.message.Message()
		msg['Subject'] = 'Consulta tus compras'		
		
		msg['From'] = 'j.jassdel@gmail.com'
		msg['To'] = e_mail
		password = "JaSSO123"
		msg.add_header('Content-Type', 'text/html')
		msg.set_payload(html)		
		s = smtplib.SMTP('smtp.gmail.com: 587')
		s.starttls()		
		# Login Credentials for sending the mail
		s.login(msg['From'], password)		
		s.sendmail(msg['From'], [msg['To']], msg.as_string())



		estatus.append({"estatus":"1","msj":""})

	except Exception as e:
		print(e)
		estatus.append({"estatus":"0","msj":"Ocurrio un error, intentelo nuevamente."})

	return Response(estatus)

#para los clientes que hacen compras como invitados, se les envia un token a su correo para que puedan consultar sus ventas-
@api_view(['GET'])
def api_consulta_ventas_invitado(request):
	estatus=[]	
	token=request.GET.get("token")
	print(token)
	ventas=[]
	#validamos que el token exista
	try:
		try:
			r=Recupera_pws.objects.get(session=token)
		except:
			estatus.append({"estatus":"0","msj":"El token es incorrecto."})
			return Response(estatus)
		try:
		#obtenemos el cliente del correo
			c=Cliente.objects.get(e_mail=r.e_mail)
		except:
			estatus.append({"estatus":"0","msj":"El Email no existe."})
			return Response(estatus)
		vtas=Venta.objects.filter(cliente=c)
		print(vtas)
		for v in vtas:		
			if v.link_seguimiento=='No Disponible':
				enviado=False
			else:
				enviado=True

			dv=Detalle_Venta.objects.filter(id_venta=v)
			img_1=""
			img_2=""
			img_3=""
			img_4=""
			cont=1
			for d in dv:
				if cont==4:
					img_4=fn_concatena_folio(str(d.id_producto.id))+"_1"
					cont=cont+1
				if cont==3:
					img_3=fn_concatena_folio(str(d.id_producto.id))+"_1"
					cont=cont+1
				if cont==2:
					img_2=fn_concatena_folio(str(d.id_producto.id))+"_1"
					cont=cont+1
				if cont==1:
					img_1=fn_concatena_folio(str(d.id_producto.id))+"_1"
					cont=cont+1
				
			if (cont-1)==1:
				solo_1=True
			else:
				solo_1=False

			ventas.append({"solo_1":solo_1,"img_1":img_1,"img_2":img_2,"img_3":img_3,"img_4":img_4,"enviado":enviado,"folio":v.id,"fecha":str(v.fecha.day)+"-"+str(v.fecha.month)+"-"+str(+v.fecha.year),"total":v.total,"estatus":v.id_estatus_venta.estatus_venta,"seguimiento":v.link_seguimiento})
	
		estatus.append({"estatus":1,'ventas':ventas})
	except Exception as e:
		print(e)
		estatus.append({"estatus":"0","msj":"No existen ventas para el Correo electronico indicado indicado."})
	return Response(estatus)


#actualiza la contraseña
#parametro
#		token:
#			es el token que se envio al correo y que se ligo al correo.
#		psw nuevo:
#			Es la nueva contraseña
@api_view(['POST'])
def api_cambia_psw_token(request):
	estatus=[]
	try:
		token=request.POST.get("token")
		psw_nueva=request.POST.get("psw_nueva")
		#validamos que el token exista
		try:
			r=Recupera_pws.objects.get(session=token)
			print(r.e_mail)
			#obtenemos el cliente del correo
			c=Cliente.objects.get(e_mail=r.e_mail)
			c.psw=psw_nueva
			c.save()
			print(c.psw)
			estatus.append({'estatus':"1","msj":""})
			return Response(estatus)
		except:			
			estatus.append({'estatus':'0','msj':'El token no existe, intenta nuevamente.'})
			return Response(estatus)
	except Exception as e:
		print(e)
		estatus.append({'estatus':'0','msj':'Error al actualizar la contraseña'})
	return Response(estatus)

#esta api es usada para al momento de confirmar informacion para la venta, 
#se desea cargar la informacion que se tiene registrada en la cuenta.
@api_view(['POST'])
def api_reinicia_direccion_temporal(request):
	estatus=[]
	session=request.POST.get("session")
	try:
		c=Clientes_Logueados.objects.get(session=session)
		try:
			#borramos la direccion de envio temporal que ya tiene registrada para registrar una nueva.
			Direccion_Envio_Cliente_Temporal.objects.get(session=session).delete()
		except Exception as e:
			print(e)
			print("No hay Direccion temporal")
		#obtenemos la direccion de envio de cliente, la que tiene registrada en la cuenta.
		de=Direccion_Envio_Cliente.objects.get(cliente=c.cliente)		
		#Insertamos la informacion de la cuenta del cliente, para que sea mostrada por default al momento de terminar la venta,
		#esta infmormacion podra ser modificada por el cliente.		
		Direccion_Envio_Cliente_Temporal.objects.create(session=session,nombre=c.cliente.nombre,apellido_p=c.cliente.apellido_p,apellido_m=c.cliente.apellido_m,telefono=c.cliente.telefono,e_mail=c.cliente.e_mail,rfc=c.cliente.rfc,calle=de.calle,numero_interior=de.numero_interior,numero_exterior=de.numero_exterior,cp=de.cp,municipio=de.municipio,estado=de.estado,pais=de.pais,	referencia=de.referencia)
		estatus.append({"estatus":"1","msj":""})
	except Exception as e:
		print(e)
		estatus.append({'estatus':"0","msj":"Error al consultar la informacion de su cuenta."})
	return Response(estatus) 

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

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
				
			nombre=request.POST.get("nombre")
			apellido_p=request.POST.get("apellido_p")
			apellido_m=request.POST.get("apellido_m")
			telefono=request.POST.get("telefono")				
			e_mail=request.POST.get("e_mail")
			rfc=request.POST.get("rfc")
			psw=request.POST.get("psw")
		
			numero_interior=request.POST.get("numero_interior")
			numero_exterior=request.POST.get("numero_exterior")
			calle=request.POST.get("calle_reg")
			cp=request.POST.get("cp")
			municipio=request.POST.get("municipio")
			estado=request.POST.get("estado")
			pais=request.POST.get("pais")		
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
					print(d_e)
					d_e.numero_interior=numero_interior
					d_e.numero_exterior=numero_exterior
					d_e.calle=calle
					d_e.cp=cp
					d_e.municipio=municipio
					d_e.estado=estado
					d_e.pais=pais
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
					c=Cliente(psw=psw,nombre=nombre,apellido_p=apellido_p,apellido_m=apellido_m,telefono=telefono,e_mail=e_mail,rfc=rfc)
					c.save()			
					d_e=Direccion_Envio_Cliente(cliente=c,numero_interior=numero_interior,numero_exterior=numero_exterior,calle=calle,cp=cp,municipio=municipio,estado=estado,pais=pais,referencia=referencia)
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
	e_mail=request.POST.get("e_mail")
	psw=request.POST.get("psw")
	session=request.POST.get("session")	

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
		estatus.append({"rfc":c_l.cliente.rfc,"e_mail":c_l.cliente.e_mail,"telefono":c_l.cliente.telefono,"estatus":"1","nombre":c_l.cliente.nombre,"apellido_p":c_l.cliente.apellido_p,"apellido_m":c_l.cliente.apellido_m,"calle":dir.calle,"numero_interior":dir.numero_interior,"numero_exterior":dir.numero_exterior,"cp":dir.cp,"municipio":dir.municipio,"estado":dir.estado,"pais":dir.pais,"referencia":dir.referencia})		
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
		print(request.method)
		if request.method=="POST":
			session=request.POST.get("session")	
			nombre=request.POST.get("nombre")
			apellido_p=request.POST.get("apellido_p")
			apellido_m=request.POST.get("apellido_m")
			telefono=request.POST.get("telefono")				
			e_mail=request.POST.get("e_mail")
			rfc=request.POST.get("rfc")	
			numero_interior=request.POST.get("numero_interior")
			numero_exterior=request.POST.get("numero_exterior")
			calle=request.POST.get("calle")
			cp=request.POST.get("cp")
			municipio=request.POST.get("municipio")
			estado=request.POST.get("estado")
			pais=request.POST.get("pais")		
			referencia=request.POST.get("referencia")		
			#borramos la direccion de envio que ya tiene esa session
			Direccion_Envio_Cliente_Temporal.objects.filter(session=session).delete()
			print("borro")
			#insertamos la direccion de envio vinculanda a la session
			Direccion_Envio_Cliente_Temporal.objects.create(session=session,nombre=nombre,apellido_p=apellido_p,apellido_m=apellido_m,telefono=telefono,e_mail=e_mail,rfc=rfc,numero_interior=numero_interior,numero_exterior=numero_exterior,calle=calle,cp=cp,municipio=municipio,estado=estado,pais=pais,referencia=referencia)
			estatus.append({"estatus":"1","msj":"Se guardo correctamente la direccion."})
		if request.method=="GET":
			session=request.GET.get("session")				
			d=Direccion_Envio_Cliente_Temporal.objects.get(session=session)			
			estatus.append({"estatus":"1","msj":"Se guardo correctamente la direccion.","nombre":d.nombre,"apellido_p":d.apellido_p,"apellido_m":d.apellido_m,"telefono":d.telefono,"e_mail":d.e_mail,"rfc":d.rfc,"numero_interior":d.numero_interior,"numero_exterior":d.numero_exterior,"calle":d.calle,"cp":d.cp,"municipio":d.municipio,"estado":d.estado,"pais":d.pais,"referencia":d.referencia})
	except Exception as e:	
		print(e)
		estatus.append({"estatus":"0","msj":"Error al guardar la direccion de envio,intente nuevamente."})
	return Response(estatus)
			
@api_view(['POST'])
def api_e_mail_notificacion(request):
	estatus=[]
	try:
		e_mail=request.POST.get("e_mail")
		print(e_mail)
		try:			
			E_Mail_Notificacion.objects.get(e_mail=e_mail)
			estatus.append({"estatus":"1","msj":"El E-Mail ya ha sido registrado."})
		except Exception as e:
			E_Mail_Notificacion.objects.create(e_mail=e_mail)
			estatus.append({"estatus":"1","msj":"Te Subscribiste Corecctamente."})
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
def api_actualiza_contraseña(request):
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
def api_solicita_recupera_psw(request):
	estatus=[]
	try:
		e_mail=request.POST.get("e_mail")
		session=request.POST.get("session")

		try:#validamos que exista el email en nuestrs cuentas
			Cliente.objects.get(e_mail=e_mail)
		except:
			#si llega aqui es porque el e_mail no existe.
			estatus.append({"estatus":0,"msj":"El E-Mail no existe en la base de datos."})
			return Response(estatus)

		#borramos todas los registros de el email recibido
		Recupera_pws.objects.filter(e_mail=e_mail).delete()

		#borramos todas los registros de la session recibida
		Recupera_pws.objects.filter(session=session).delete()
		
		Recupera_pws.objects.create(session=session,e_mail=e_mail)
		
		#se envia el correo con el codigo de seguridad.		
		email = EmailMessage('Solicitud Cambio Contraseña', 'Introduce este token en el formulario de cambio de contraseña: '+session, to=[e_mail])
		email.send()	
		estatus.append({"estatus":"1","msj":""})

	except Exception as e:
		print(e)
		estatus.append({"estatus":"0","msj":"Ocurrio un error, intentelo nuevamente."})

	return Response(estatus)
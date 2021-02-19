
from django.views.generic.edit import FormView
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth import logout
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from seguridad.models import Direccion_Envio_Cliente,Clientes_Logueados,Direccion_Envio_Cliente_Temporal
from seguridad.models import E_Mail_Notificacion,Recupera_pws
from django.core.mail import EmailMessage
#from ventas.models import Venta,Detalle_Venta
from django.conf import settings
import smtplib
import email.message
from .forms import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.models  import Permission,User
from empenos.models import User_2,Cajas,Perfil,Sucursal
from datetime import date, datetime, time
from random import randint

IP_LOCAL = settings.IP_LOCAL

encabezado_link_consulta_venta_1="""

<html>
    <head>           
    </head>
    <body style="background-color:#e9e9e9;">
        <table style="width: 300px;; margin:0 auto;background-color: white;"  cellpadding="10" cellspacing="0">
            <tr style="background-color: black;">
                <td colspan="6">
                        <img src="https://www.jassdel.com/assets/img/logo_peque.jpg" style="width: 50px;">
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
def Login(request):
		#en caso de que ya este logueado, lo redireccionamos a la pantalla de bienvenidos.
	if request.user.is_authenticated:
		
		return HttpResponseRedirect("/bienvenidos")

	if request.method=="POST":
		usuario=request.POST.get("usuario")
		password=request.POST.get("password")
		user=authenticate (request,username=usuario,password=password)
		if user is not None:

			login(request,user)

			#si el usuario y contraseña son correctas pero el perfil no es el correcto, bloquea el acceso.
			try:
				user_2=User_2.objects.get(user=user)
			except:
				
				form=Login_Form(request.POST)
				estatus=0
				msj="La cuenta del usuario esta incompleta1."			
				return render(request,'login.html',locals())
			
			#cada que iniciamos sesion, se genera un nuevo folio.
			user_2.sesion=fn_genera_sesion()
			user_2.save()

			estatus=1			
			
			form=Login_Form()
			return HttpResponseRedirect(reverse('seguridad:login'))
			#return HttpResponseRedirect("/bienvenidos")
		else:
			form=Login_Form(request.POST)
			#mandamos mensaje de error
			estatus=0
			msj="El usuario y contraseña no coinciden."			
			return render(request,'login.html',locals())
	else:
		form=Login_Form()
		return render(request,'login.html',locals())
	
def cerrar_session(request):

	logout(request)
	return HttpResponseRedirect("/")

#direccionamos a esta pantalla cuando el usuario no tenga acceso a una opcion.
def sin_permiso_de_acceso(request):
	return render(request,'seguridad/sin_permiso_de_acceso.html',locals())
 
def bienvenidos(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	if caja != None:
		c=caja.caja
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para no dejar entrar a la pantalla.




	return render(request,'seguridad/bienvenidos.html',locals())

def admin_user(request):
	return render(request,'seguridad/admin_user.html',{})

def admin_administracion(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	caja_abierta="0"
	caja=Cajas

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	if caja != None:
		c=caja.caja
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para no dejar entrar a la pantalla.


	IP_LOCAL = settings.IP_LOCAL
	id_usuario=user_2.user.id

	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max) 



	return render(request,'seguridad/admin_administracion.html',locals())	

def admin_catalogos(request):
	return render(request,'seguridad/admin_catalogos.html',{})

def admin_productos(request):
	return render(request,'seguridad/admin_stock.html',{})

"""
idpermiso = 3
"""
def admin_permisos_usuario(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(3):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	try:
		c=caja.caja
	except:
		c=""


	id_usuario_modifica = request.user.id
	return render(request,'seguridad/admin_permisos_usuario.html',locals())


def admin_ventas(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	if caja != None:
		c=caja.caja
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para no dejar entrar a la pantalla.


	return render(request,'seguridad/admin_ventas.html',locals())

def admin_perfil(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	if caja != None:
		c=caja.caja
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para no dejar entrar a la pantalla.


	return render(request,'seguridad/admin_perfil.html',locals())

def admin_cajas(request):


	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()


	if caja != None:
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja
	else:
		caja_abierta="0"
		caja=Cajas


	return render(request,'seguridad/admin_cajas.html',locals())

def admin_empenos(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	c = ""
	if caja != None:
		c=caja.caja
	return render(request,'seguridad/admin_empenos.html',locals())

def admin_reportes(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	c = ""
	if caja != None:
		c=caja.caja

	return render(request,'seguridad/admin_reportes.html',locals())

def permisos(request):
	if request.method=="POST":
		form=Permisos_Form(request.POST)
	else:
		permisos=Permission.objects.filter(name__icontains="p_")
		form=Permisos_Form()
	return render(request,'seguridad/consulta_permisos.html',locals())

def cambio_psw_usr(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	if caja != None:
		c=caja.caja
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para no dejar entrar a la pantalla.


	IP_LOCAL = settings.IP_LOCAL
	id_usuario=user_2.user.id




	


	if request.method=="POST":
		
		psw=request.POST.get("psw")

		usr=request.user
		usr.set_password(psw)
		usr.save()
		user=authenticate (request,username=usr.username,password=psw)
		
		login(request,user)

		actualizado="1"
	else:
		
		actualizado="0"
	form=Cambia_Psw_Form()
	return render(request,'seguridad/cambio_psw_usr.html',locals())


def cambio_sucursal(request):

	#si no esta logueado mandamos al login
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('seguridad:login'))
	
	#si el usuario y contraseña son correctas pero el perfil no es el correcto, bloquea el acceso.
	try:
		user_2=User_2.objects.get(user=request.user)
	except Exception as e:		
		form=Login_Form(request.POST)
		estatus=0
		msj="La cuenta del usuario esta incompleta."			
		return render(request,'login.html',locals())
	IP_LOCAL = settings.IP_LOCAL
	id_usuario=user_2.user.id

	c=""


	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	
	msj_error=""	
	try:
		#validamos si el usuaario tiene caja abierta para mostrarla en el encabezado.
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=request.user)

		c=caja.caja
	except Exception as e:
		msj_error="No cuentas con caja abierta."
		print(e)
		c="CERRADA"



	exito="2"
	if request.method=="POST":
		try:
			id_usuario=request.POST.get("usuario")
			id_sucursal=request.POST.get("sucursal")

			sucursal=Sucursal.objects.get(id=id_sucursal)
			usuario=User.objects.get(id=id_usuario)

			u2=User_2.objects.get(user=usuario)
			u2.sucursal=sucursal
			u2.save()

			form=Cambio_Sucursal_Form()
			exito="1"
		except:
			exito="0"
	else:
		exito="2"
		form=Cambio_Sucursal_Form()
	return render(request,'seguridad/cambio_sucursal.html',locals())

"""

id_permiso = 1
cuando se recibe id
id_permiso = 2
"""
def alta_usuario(request,id=None):
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	caja_abierta="0"
	caja=Cajas
	
	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	if caja != None:
		c=caja.caja
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para no dejar entrar a la pantalla.


	#validamos si tiene acceso a esta opcion.
	#cuando id es none, es que es alta
	if id == None:
		if not user_2_1.fn_tiene_acceso_a_vista(1):
			return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))
	else:#cuando id no es none, es consulta y edicion.
		if not user_2_1.fn_tiene_acceso_a_vista(2):
			return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()



	
	msj_error = ""
	#el estatus 1 indica que todo esta ok, 
	#el estatus 0 indica que se presento un error. el error debe venir acompalñado de una leyenda en la variable msj_error
	estatus = "1" 


	is_edicion = "0"

	user_name = ""
	first_name = ""
	last_name = ""
	id_perfil = ""
	id_sucursal = ""

	#obtenemos el objeto a editar
	if id != None :
		#obtenemos el objeto a editar
		usr=User.objects.get(id=id)
		is_edicion = "1"
		encabezado = "Edicion del usuario: " + usr.username 

		u2 = User_2.objects.get(user = usr)

		user_name = usr.username
		first_name = usr.first_name
		last_name = usr.last_name
		id_perfil = u2.perfil.id
		id_sucursal = u2.sucursal.id
		activo = usr.is_active

	else:
		is_edicion = "0"
		encabezado = "Alta de usuario"

	id_usuario = request.user.id
	form=User_Form()

	return render(request,'seguridad/alta_usuario.html',locals())


"""
id = 2
"""
def consulta_usuarios(request):
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(2):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	if request.method=="POST":
		form=Busca_Usuario_Form(request.POST)
		if request.POST.get("username")=="":
			usuarios=User.objects.all()
		else:
			usuarios=User.objects.filter(username__icontains=request.POST.get("username"))
	else:
		form=Busca_Usuario_Form()
		usuarios=User.objects.all()
	return render(request,'seguridad/consulta_usuarios.html',locals())



#esta api recibe la session y la desvincula de la cuenta logueada,
#esto con la finalidad de no perder los carritos agregados al carrito de compras.
"""@api_view(['POST'])
def api_kill_session(request):
	error=[]
	if request.method=="POST":
		session=request.POST.get("session")
		Clientes_Logueados.objects.get(session=session).delete()
	return Response(error)
"""

#api para crear cuentas de clientes
#en caso de ya existir, actualiza la cuenta.
#	En caso de que se reciba la session, es porque se trata de un actualizacion a un cliente
#	En caso de que no se reciba la session, es porque es un cliente nuevo.
"""@api_view(['POST'])
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

"""

"""
#api para identificar al usuario
@api_view(["POST"])
def api_login_usuario(request):
	cliente=[]	
	e_mail=request.POST.get("e_mail").upper()
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
"""		
@api_view(['POST'])
def api_e_mail_notificacion(request):
	estatus=[]
	try:
		e_mail=request.POST.get("e_mail").upper()
		
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
"""
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
"""
#en esta api se llena la tabla creando la relacion del token con el email del que se desea recuperar la contraseña,
#para posteriormente enviar el correo con el link para actualizar la contraseña.
#parametros
#		token: es el token unico que nos ayudara a crear el link para cambiar contraseña,
#				este token se liga al correo
#		e_mail:	Es el email de la cuenta que se desea cambiar contraseña.
"""
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

		link=settings.URL_LOCAL_FRONTEND+"listado_ventas/"+session

		html=encabezado_link_consulta_venta_1+link+encabezado_link_consulta_venta_2
		html = html.replace("\xe9", "e")
		html = html.replace("\x0a", "\n")
		server = smtplib.SMTP('smtp.gmail.com:587')
		msg = email.message.Message()
		msg['Subject'] = 'Consulta tus compras'		
		
		msg['From'] = 'j.jassdel@gmail.com'
		msg['To'] = e_mail
		password = settings.EMAIL_HOST_PASSWORD
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
"""

#actualiza la contraseña
#parametro
#		token:
#			es el token que se envio al correo y que se ligo al correo.
#		psw nuevo:
#			Es la nueva contraseña
"""
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
			
			estatus.append({'estatus':"1","msj":""})
			return Response(estatus)
		except:			
			estatus.append({'estatus':'0','msj':'El token no existe, intenta nuevamente.'})
			return Response(estatus)
	except Exception as e:
		print(e)
		estatus.append({'estatus':'0','msj':'Error al actualizar la contraseña'})
	return Response(estatus)
"""
#esta api es usada para al momento de confirmar informacion para la venta, 
#se desea cargar la informacion que se tiene registrada en la cuenta.
"""
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
"""
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


def fn_genera_sesion():
	session=""
	session=str(randint(0,9))	
	session=session+str(randint(0,9))	
	session=session+str(randint(0,9))	
	session=session+str(randint(0,9))	
	session=session+str(randint(0,9))	
	session=session+str(randint(0,9))	
	session=session+str(randint(0,9))	
	return int(session)

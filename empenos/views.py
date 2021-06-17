from Xavis.settings import IDENTIFICADOR_TIENDA
from re import I, S
from django.shortcuts import render
from empenos.models import *
from seguridad.forms import Login_Form
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from empenos.forms import *
from django.db import transaction
from datetime import date, datetime, time,timedelta
from django.db.models import Sum
from random import randint
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.pagesizes import A4
import math
from empenos.funciones import *
from empenos.report import *
import decimal
import csv
import smtplib
import email.message

IP_LOCAL = settings.IP_LOCAL
LOCALHOST=settings.LOCALHOST
IDENTIFICADOR_TIENDA = settings.IDENTIFICADOR_TIENDA

@transaction.atomic
def abrir_caja(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)

	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#estatus 0: indica error
	#estatus 1: indica todo ok
	#estatus 2: indica todo nada
	estatus = "2" 
	msj_error = ""

	hoy = date.today()
	hoy_min = datetime.combine(hoy,time.min)
	hoy_max = datetime.combine (hoy,time.max)

	#obtenemos la sucursal por default del cliente.
	sucursal = user_2.sucursal

	#validamos que la sucursal no cuente con caja abierta en el dia.

	try:
		#Si existe caja no permite entrada
		caja = Cajas.objects.get(sucursal = sucursal, fecha__range = (hoy_min,hoy_max))
		estatus = "0"
		msj_error = "La sucursal ya aperturo caja el dìa de hoy. Si ya fue cerrada, solicite reapertura"
		return render(request,'empenos/abre_caja.html',locals())
	except Exception as e:
		print(e)
		pass

	#validamos que la sucursal no cuente con caja abierta en dias anteriores
	try:
		caja = Cajas.objects.get(sucursal = sucursal,fecha_cierre__isnull = True)
		estatus = "0"
		msj_error = "La sucursal cuenta con caja abierta en dias anteriores. Cierrela para poder abrir nuevamente hoy."
		return render(request,'empenos/abre_caja.html',locals())
	except:
		pass

	#obtenemos el importe con el que se aperturara la caja.
	#sucursal.saldo

	if request.method == "POST":
		r = sucursal.fn_abre_caja(sucursal.saldo,request.user)
		if r[0]:
			estatus = "1"
		else:
			estatus = "0"
			msj_error = r[1]						
			return render(request,'empenos/abre_caja.html',locals())

	return render(request,'empenos/abre_caja.html',locals())


	"""
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

	caja_abierta="0"


	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	#si la tienda ya cuenta con una caja abierta, no le permitimos abrir otra hasta
	caja=Cajas.objects.filter(fecha_cierre__isnull=True,sucursal=user_2.sucursal)

	msj_caja=""
	if caja.exists():
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para no dejar entrar a la pantalla.
		msj_caja="La sucursal cuenta con caja abierta, para seguir operando realice el corte de caja."

	caja_2=Cajas.objects.filter(fecha__range=(min_pub_date_time,max_pub_date_time),sucursal=user_2.sucursal)

	if caja_2.exists():
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para no dejar entrar a la pantalla.
		msj_caja="Solo se puede abrir una caja por dia en la sucursal, si ya fue cerrada, solicite la reapertura para seguir operando."

	sucursales = Sucursales_Regional.objects.filter(user=user_2.user,sucursal=user_2.sucursal)
	
	id_sucursal=0
	if user_2.perfil.id==1 or user_2.perfil.id==2:
		#si es valuador o gerente de sucursal ponemos su sucursal por default
		id_sucursal=user_2.sucursal.id
	

	exito="2"
	#si es post y no tenemos caja abierta
	if request.method=="POST" and caja_abierta=="0":

		try:
			suc=Sucursal.objects.get(id=request.POST["sucursal"])
			#buscamos la caja que se abrira
			caja=fn_nueva_caja(suc)

			tm=Tipo_Movimiento.objects.get(id=1)
			folio=fn_folios(tm,suc)
			str_folio=fn_str_clave(folio)

			form=Abre_Caja_Form(request.POST)
			if form.is_valid():
				f=form.save( commit=False)
				f.folio=str_folio
				f.caja=caja
				c=caja
				f.fecha=datetime.today()
				f.diferencia=f.importe
				f.importe=user_2.sucursal.saldo
				f.save()

				#cuando un gerente de sucursal abre caja, se le marca la tienda en la que abrio caja.
				user_2.sucursal=suc
				user_2.save()
				
				#return HttpResponseRedirect(reverse('seguridad:admin_cajas'))
			exito="1"
		except Exception as e:
			print("Error al abrir la caja.")
			exito="0"

			
	else:
		form=Abre_Caja_Form()
	"""


#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

@transaction.atomic
def abona_apartado(request,id_apartado):
	hoy = date.today()
	hoy_inicial = datetime.combine(hoy, time.min) 
	hoy_final = datetime.combine(hoy, time.max)  

	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#buscamos la configuracion del negocio para apartados
	apartado = Apartado.objects.get(id = id_apartado)	


	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	if caja == None:
		caja_abierta = "0"
		caja = Cajas
	else:
		caja_abierta = "1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc = caja.sucursal
		c = caja.caja

	usuario=request.user

	apartado = Apartado.objects.get(id = id_apartado)	

	no_apartado = "1"
	if apartado.estatus.id != 1:
		no_apartado = "0"
		form=Apartado_Form()		
		return render(request,'empenos/apartado.html',locals())

	det_boleta=Det_Boleto_Empeno.objects.filter(boleta_empeno=apartado.boleta)
	error="1"

	try:
		ma=Min_Apartado.objects.get(id=1)
	except Exception as e:
		print(e)
		form=Apartado_Form()
		error="0"
		msj_error="No se capturado el catalogo Min_Apartado."
		return render(request,'empenos/apartado.html',locals())


	try:
		a_criterio_cajero = Min_Apartado.objects.get(id = 1).a_criterio_cajero
	except Exception as e:
		print(e)
		error="0"
		msj_error="No tiene configurado los apartados, contacte al administrador del sistema."
		form=Apartado_Form()
		return render(request,'empenos/apartado.html',locals())


	if request.method == "POST":
		try:

			abono = request.POST.get("abono")

			ap_vendido = Estatus_Apartado.objects.get(id=3)
			vendida = Estatus_Boleta.objects.get(id=6)

			saldo_restante = int(apartado.saldo_restante)-int(abono)


			#si no es a criterio de cajero, calcula en base a configuración.
			if not a_criterio_cajero:
				#minimo para darle dos meses.
				min_apartado_2_mes=math.ceil(decimal.Decimal(apartado.importe_venta)*(decimal.Decimal(ma.porc_min_2_mes)/decimal.Decimal(100)))

				#Si el saldo restante  es mayor al minimo requerido para que diera dos meses
				#se actualiza la fecha de nacimiento
				total_abonado = decimal.Decimal(apartado.importe_venta) - decimal.Decimal(saldo_restante)
				if total_abonado >= min_apartado_2_mes:
					fecha_vencimiento = datetime.combine(fn_add_months(apartado.fecha,2), time.min)
					apartado.fecha_vencimiento = fecha_vencimiento	

			apartado.saldo_restante = saldo_restante

			#cambiamos el estatus del apartado cuando ya no quede saldo restante
			if int(saldo_restante) == 0:				
				apartado.boleta.estatus = vendida
				apartado.estatus = ap_vendido
				apartado.boleta.save()

			apartado.save()

			#es la clave para Apartado
			tm=Tipo_Movimiento.objects.get(id = 8)

			#Generamos el folio para el apartado			
			folio = fn_folios(tm,suc)

			ab_ap = Abono_Apartado()
			ab_ap.folio = folio
			ab_ap.usuario = usuario
			ab_ap.importe = abono
			ab_ap.caja = caja
			ab_ap.apartado = apartado
			ab_ap.save()

			error = "1"

			Imprime_Apartado.objects.filter(usuario = usuario).delete()
			Imprime_Apartado.objects.create(usuario = usuario,apartado = apartado,abono = ab_ap)

			#return HttpResponseRedirect(reverse('empenos:imprime_apartado'))
			form = Abono_Apartado_Form()

		except Exception as e:
			print(e)
			error = "0"
			msj_error = "Error al aplicar el abono."
			form = Abono_Apartado_Form()
			return render(request,'empenos/abona_apartado.html',locals())
	else:
		error = "2"				
		form = Abono_Apartado_Form()
	return render(request,'empenos/abona_apartado.html',locals())
#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************


"""
idpermiso = 14
"""

def administracion_porcentaje_mutuo(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(14):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	hoy = date.today()
	hoy_inicial = datetime.combine(hoy, time.min) 
	hoy_final = datetime.combine(hoy, time.max)  

	try:		
		#validamos si el usuario tiene caja abierta en el dia actual.
		caja = Cajas.objects.get(fecha__range = (hoy_inicial,hoy_final),fecha_cierre__isnull = True,usuario=request.user)
		caja_abierta = "1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc = caja.sucursal
		c = caja.caja

	except Exception as e:
		print(e)
		caja_abierta = "0"
		caja = Cajas

	permiso="1"

	estatus = "2"	

	if request.method == "POST" and permiso == "1":
		id_sucursal = request.POST.get("sucursal")
		sucursal = Sucursal.objects.get(id = id_sucursal)

		porcentaje_oro = request.POST.get("porcentaje_oro")
		porcentaje_plata = request.POST.get("porcentaje_plata")
		porcentaje_articulos_varios = request.POST.get("porcentaje_articulos_varios")

		sucursal = Sucursal.objects.get(id = int(id_sucursal))

		print(type(porcentaje_oro))
		print(porcentaje_plata)
		print(porcentaje_articulos_varios)
		resp = sucursal.fn_actualiza_porcentaje_mutuo(int(porcentaje_oro),int(porcentaje_plata),int(porcentaje_articulos_varios))

		if resp:
			estatus = "1"
		else:
			estatus = "0"


	form = Porcentaje_Mutuo_Form()
	return render(request,'empenos/administracion_porcentaje_mutuo.html',locals())

"""
idpermiso = 13
"""
def administracion_interes_empeno(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(13):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	hoy = date.today()
	hoy_inicial = datetime.combine(hoy, time.min) 
	hoy_final = datetime.combine(hoy, time.max)  

	try:		
		#validamos si el usuario tiene caja abierta en el dia actual.
		caja = Cajas.objects.get(fecha__range = (hoy_inicial,hoy_final),fecha_cierre__isnull = True,usuario=request.user)
		caja_abierta = "1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc = caja.sucursal
		c = caja.caja

	except Exception as e:
		print(e)
		caja_abierta = "0"
		caja = Cajas

	permiso="1"

	estatus = "0"#no hace nada

	if request.method == "POST":
		id_sucursal = request.POST.get("sucursal")
		sucursal = Sucursal.objects.get(id = int(id_sucursal))

		#si existe un registro, solo lo actualizamos, de lo contrario, creamos el registro.
		try:

			cie = Configuracion_Interes_Empeno.objects.get(sucursal = sucursal)

			cie.almacenaje_oro = request.POST.get("almacenaje_oro") 
			cie.interes_oro = request.POST.get("interes_oro") 
			cie.iva_oro = request.POST.get("iva_oro") 
			cie.almacenaje_plata = request.POST.get("almacenaje_plata") 
			cie.interes_plata = request.POST.get("interes_plata") 
			cie.iva_plata = request.POST.get("iva_plata") 
			cie.almacenaje_prod_varios = request.POST.get("almacenaje_art_varios") 
			cie.interes_prod_varios = request.POST.get("interes_art_varios") 
			cie.iva_prod_varios = request.POST.get("iva_art_varios") 
			cie.usuario_modifica = request.user
			cie.fecha_modificacion = date.today()
			cie.save()			

		except:
			cie = Configuracion_Interes_Empeno()
			cie.sucursal = sucursal

			cie.almacenaje_oro = request.POST.get("almacenaje_oro") 
			cie.interes_oro = request.POST.get("interes_oro") 
			cie.iva_oro = request.POST.get("iva_oro") 
			cie.almacenaje_plata = request.POST.get("almacenaje_plata") 
			cie.interes_plata = request.POST.get("interes_plata") 
			cie.iva_plata = request.POST.get("iva_plata") 
			cie.almacenaje_pro_varios = request.POST.get("almacenaje_art_varios") 
			cie.interes_prod_varios = request.POST.get("interes_art_varios") 
			cie.iva_prod_varios = request.POST.get("iva_art_varios") 
			cie.usuario_modifica = request.user
			cie.fecha_modificacion = date.today()
			cie.save()	
		estatus = "1"#muestra mensaje de que se guardo con exito

	else:
		estatus = "0"

		

	

		

	

	form = Interes_Empeno_Form()
	return render(request,'empenos/administracion_interes_empeno.html',locals())

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
"""
idPermiso = 5
"""
def admin_min_apartado(request,id):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
	#validamos si tiene permisos para acceder a esta opcion.
	if not user_2.fn_tiene_acceso_a_vista(5):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))


	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	try:		
		#validamos si el usuario tiene caja abierta en el dia actual.
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=request.user)
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja

	except Exception as e:
		print(e)
		caja_abierta="0"
		caja=Cajas

	permiso="1"

	try:
		query=Min_Apartado.objects.get(id=int(id))
	except:
		query=Min_Apartado()

	estatus="0"
	if request.method=="POST":
		if permiso=="0":#si no cuenta con permiso no puede guardar
			estatus="0"#fallo al guardar 
		else:
			try:
				form=Min_Apartado_Form(request.POST,instance=query)
				
				if form.is_valid():
					f = form.save(commit = False)
					f.usuario_modifica = request.user
					f.save()
					estatus="1"#guardo con exito
				else:
					estatus="0"#fallo al guardar 
			except Exception as e:
				estatus="0"#fallo al guardar 
				print(e)
				form=Min_Apartado_Form(instance=query)
	else:
		estatus="2"#es GET, no valida error.
		form=Min_Apartado_Form(instance=query)

	return render(request,'empenos/admin_min_apartado.html',locals())

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
def admin_precio_venta(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(8):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	caja = user_2.fn_tiene_caja_abierta()

	if caja != None:
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja
	else:
		caja_abierta="0"
		caja=Cajas

	form = Establece_Precio_Venta_Form()
	id_usuario = request.user.id
	return render(request,'empenos/admin_precio_venta.html',locals())
#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
"""
idpermiso = 12
"""
def concepto_retiro(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(12):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	user_2_1 = User_2.objects.get(user = user_2.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2_1.fn_tiene_caja_abierta()

	if caja == None:
		caja_abierta="0"
		caja=Cajas
	else:
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja




	#solo el gerente regional tiene permiso para acceder a esta opción	
	permiso = "1"

	form = Alta_Concepto_Retiro_Form()	
	id_usuario = user_2.user.id

	sucursales = Sucursal.objects.filter().exclude(id = user_2.sucursal.id)

	return render(request,'empenos/concepto_retiro.html',locals())


#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
@transaction.atomic
def apartado(request):

	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	IP_LOCAL = settings.IP_LOCAL

	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	if caja == None:
		caja_abierta="0"
		caja=Cajas
	else:
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja



	username=request.user.username
	id_sucursal=user_2.sucursal.id

	estatus="0"
	msj_error=""

	try:
		a_criterio_cajero = Min_Apartado.objects.get(id = 1).a_criterio_cajero
	except Exception as e:
		print(e)
		estatus="0"
		msj_error="No tiene configurado los apartados, contacte al administrador del sistema."
		form=Apartado_Form()
		return render(request,'empenos/apartado.html',locals())

	if request.method=="POST":

		if request.POST.get("nombre_cliente") == "":
			estatus="0"
			msj_error="Debe seleccionar el cliente."
			form=Apartado_Form()
			return render(request,'empenos/apartado.html',locals())


		ma=Min_Apartado.objects.get(id=1)

		try:
			usuario=request.user
			
			#es la clave para Apartado
			tm = Tipo_Movimiento.objects.get(id=7)

			#Generamos el folio para el apartado			
			folio = fn_folios(tm,suc)

			boleta = Apartado_Temporal.objects.get(usuario=usuario).boleta

			estatus_apartado = Estatus_Apartado.objects.get(id=1)

			importe_venta = math.ceil(boleta.fn_calcula_precio_apartado())


			hoy = datetime.combine(pub_date, time.min) 

			if a_criterio_cajero:
					
				pago_cliente_2 = int(request.POST.get("pago_cliente_2"))
				num_meses_apartar = int(request.POST.get("num_meses_apartar"))

				pago_cliente = pago_cliente_2
				fecha_vencimiento = datetime.combine(fn_add_months(hoy,num_meses_apartar), time.min)

				if int(pago_cliente) >= int(importe_venta):
					form=Apartado_Form()
					estatus="0"
					msj_error="El importe ingresado cubre en su totalidad el costo del producto, realice la operación en la opción de venta piso."
					return render(request,'empenos/apartado.html',locals())


			else:
				pago_cliente = int(request.POST.get("pago_cliente"))
				if int(pago_cliente) >= int(importe_venta):
					form=Apartado_Form()
					estatus="0"
					msj_error="El importe ingresado cubre en su totalidad el costo del producto, realice la operación en la opción de venta piso."
					return render(request,'empenos/apartado.html',locals())


				min_apartado_2_mes=math.ceil(decimal.Decimal(importe_venta)*(decimal.Decimal(ma.porc_min_2_mes)/decimal.Decimal(100)))

				

				#si el pago cliente es mayor al minimo para dos meses, se le da dos meses de apartado,
				# de lo contrario solo se le da 1
				if pago_cliente>=min_apartado_2_mes:
					fecha_vencimiento=datetime.combine(fn_add_months(hoy,2), time.min)
				else:
					fecha_vencimiento=datetime.combine(fn_add_months(hoy,1), time.min)
				

 

			#para asegurarnos que no se venza en dia de azueto
			fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

			valida_boleta=Apartado.objects.filter(boleta=boleta)

			#SILA BOLETA NO HA SIDO APARTADA, VALIDAMOS QUE NO SE HAYA VENDIDO EN VENTA PISO
			if not valida_boleta.exists():			

				valida_boleta = Det_Venta_Piso.objects.filter(boleta = boleta)			

				#si no ha sido venida en venta piso, validamos que tampoco se ahaya vendido en venta a granel
				if not valida_boleta.exists():			

					valida_boleta = Det_Venta_Granel.objects.filter(boleta = boleta)

			if valida_boleta.exists():
				form=Apartado_Form()
				estatus="0"
				msj_error="La boleta ya no esta disponible para ser apartada."
				Apartado_Temporal.objects.get(usuario=usuario).delete()
				return render(request,'empenos/apartado.html',locals())

			



			with transaction.atomic():
				ap=Apartado()
				ap.folio=folio
				ap.usuario=usuario
				ap.importe_venta=importe_venta
				ap.caja=caja
				ap.cliente = None
				ap.nombre_cliente = request.POST.get("nombre_cliente")
				ap.telefono = request.POST.get("telefono")
				ap.estatus=estatus_apartado
				ap.boleta=boleta
				ap.fecha_vencimiento=fecha_vencimiento
				ap.saldo_restante=math.ceil(decimal.Decimal(importe_venta)-decimal.Decimal(pago_cliente))
				ap.sucursal=suc
				ap.save()

				#es la clave para Apartado
				tm=Tipo_Movimiento.objects.get(id=8)

				#Generamos el folio para el apartado			
				folio=fn_folios(tm,suc)
				ab_ap=Abono_Apartado()
				ab_ap.folio=folio
				ab_ap.usuario=usuario
				ab_ap.importe=pago_cliente
				ab_ap.caja=caja
				ab_ap.apartado=ap
				ab_ap.save()

				Apartado_Temporal.objects.get(usuario=usuario).delete()

				#estatus apartado para la boleta
				estatus_boleta=Estatus_Boleta.objects.get(id=7)

				boleta.estatus=estatus_boleta
				boleta.save()

				Imprime_Apartado.objects.filter(usuario=usuario).delete()
				Imprime_Apartado.objects.create(usuario=usuario,apartado=ap,abono=ab_ap)
				estatus = "1"

			#return HttpResponseRedirect(reverse('empenos:imprime_apartado'))
		except Exception as e:
			print(e)
			estatus="0" 
			msj_error="Error al apartar el producto."
			form=Apartado_Form()
			transaction.set_rollback(True)
			return render(request,'empenos/apartado.html',locals())
	else:
		
		
		estatus="2"
	form=Apartado_Form()
	return render(request,'empenos/apartado.html',locals())


#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************


def re_imprimir_apartado(request,id_apartado):
	apartado=Apartado.objects.get(id=id_apartado)
	Imprime_Apartado.objects.filter(usuario=request.user).delete()
	Imprime_Apartado.objects.create(usuario=request.user,apartado=apartado)
	return rep_imprime_apartado(request)
	#return imprime_apartado(request)


#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

def imprime_apartado(request):
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename=hello.pdf'

	im=Imprime_Apartado.objects.get(usuario=request.user)

	#obtenemos el abono a imprimir.
	#abono=Imprime_Abono.objects.get(usuario=request.user).abono
	buffer=BytesIO()

	p=canvas.Canvas(buffer,pagesize=A4)

	heigth_row=20#cada renglon es de 20.

	current_row=730

	p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg' , 40, 720, 200, 60)
	p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 40, 720-380, 200, 60)
	p.setFont("Helvetica-Bold",12)
	p.drawString(250,770-380,"Copia cliente")
	p.setFont("Helvetica-Bold",12)
	p.drawString(400,760,"Folio apartado: "+str(im.apartado.folio))
	p.drawString(400,360,"Folio apartado: "+str(im.apartado.folio))

	p.setFont("Helvetica-Bold",12)
	p.drawString(250,730,"Apartado Producto")
	p.drawString(250,340,"Apartado Producto")

	current_row=current_row-20
	p.setFont("Helvetica",10)

	current_row=current_row-20
	p.drawString(55,current_row,"Folio boleta:")
	p.drawString(130,current_row,str(im.apartado.boleta.folio))

	p.drawString(55,current_row-380,"Folio boleta:")
	p.drawString(130,current_row-380,str(im.apartado.boleta.folio))

	p.drawString(360,current_row,"Cajero: " + request.user.username)
	p.drawString(360,current_row-380,"Cajero: " + request.user.username)

	current_row=current_row-20

	p.drawString(360,current_row,"Fecha emisión: ")
	p.drawString(430,current_row,str(im.apartado.fecha.strftime("%Y-%m-%d %H:%m")))

	p.drawString(360,current_row-380,"Fecha emisión: ")
	p.drawString(430,current_row-380,str(im.apartado.fecha.strftime("%Y-%m-%d %H:%m")))

	
	p.drawString(55,current_row,"Fecha vencimiento: ")
	p.drawString(150,current_row,str(im.apartado.fecha_vencimiento.strftime("%Y-%m-%d")))

	p.drawString(55,current_row-380,"Fecha vencimiento: ")
	p.drawString(150,current_row-380,str(im.apartado.fecha_vencimiento.strftime("%Y-%m-%d")))

	current_row=current_row-20
	p.drawString(360,current_row,"Sucursal:")
	p.drawString(430,current_row,im.apartado.caja.sucursal.sucursal)

	p.drawString(360,current_row-380,"Sucursal:")
	p.drawString(430,current_row-380,im.apartado.caja.sucursal.sucursal)

	
	p.setFont("Helvetica",10)
	p.drawString(55,current_row,"Cliente: ")
	p.setFont("Helvetica",10)
	p.drawString(100,current_row,im.apartado.nombre_cliente)
	p.setFont("Helvetica",10)

	p.drawString(55,current_row-380,"Cliente: ")
	p.setFont("Helvetica",10)
	p.drawString(100,current_row-380,im.apartado.nombre_cliente)
	p.setFont("Helvetica",10)
	current_row=current_row-20
	current_row=current_row-20

	p.setFont("Helvetica-Bold",10)
	p.drawString(55,current_row,"Artículo")
	p.drawString(480,current_row,"Precio")

	p.drawString(55,current_row-380,"Artículo")
	p.drawString(480,current_row-380,"Precio")

	p.setFont("Helvetica",8)
	current_row=current_row-20

	
	
	dbe=Det_Boleto_Empeno.objects.filter(boleta_empeno=im.apartado.boleta)

	importe="$"+"{:0,.2f}".format(math.ceil(im.apartado.importe_venta))


	p.drawString(480,current_row,importe)
	p.drawString(480,current_row-380,importe)

	for db in dbe:
		p.drawString(55,current_row,db.descripcion)
		p.drawString(55,current_row-380,db.descripcion)
		current_row=current_row-20		
		
		if db.observaciones is not None:				
			p.drawString(55,current_row,db.observaciones)
			p.drawString(55,current_row-380,db.observaciones)
			current_row=current_row-20		

		



	p.setFont("Helvetica-Bold",10)	
	p.drawString(380,current_row,"Costo Total: ")
	p.drawString(380,current_row-380,"Costo Total: ")
	importe_venta="$"+"{:0,.2f}".format(math.ceil(im.apartado.importe_venta))	
	p.drawString(480,current_row,importe_venta)
	p.drawString(480,current_row-380,importe_venta)

	#cuando no contiene abono, es porque es una reimpresion y no hay abono actual.
	if im.abono!=None:
		current_row=current_row-20

		p.setFont("Helvetica-Bold",10)	
		p.drawString(380,current_row,"Abono: ")
		p.drawString(380,current_row-380,"Abono: ")

		importe="$"+"{:0,.2f}".format(int(im.abono.importe))	
		p.drawString(480,current_row,importe)
		p.drawString(480,current_row-380,importe)


	aa=Abono_Apartado.objects.filter(apartado=im.apartado).aggregate(Sum("importe"))

	total_abonado=0.00
	if aa["importe__sum"]!=None:
		total_abonado=aa["importe__sum"]

	current_row=current_row-20

	p.setFont("Helvetica-Bold",10)	
	p.drawString(380,current_row,"Total Abonado: ")
	p.drawString(380,current_row-380,"Total Abonado: ")
	total_abonado="$"+"{:0,.2f}".format(int(total_abonado))	
	p.drawString(480,current_row,total_abonado)
	p.drawString(480,current_row-380,total_abonado)

	current_row=current_row-20

	p.setFont("Helvetica-Bold",10)	
	p.drawString(380,current_row,"Restan: ")
	p.drawString(380,current_row-380,"Restan: ")
	saldo_restante="$"+"{:0,.2f}".format(math.ceil(im.apartado.saldo_restante))	
	p.drawString(480,current_row,saldo_restante)
	p.drawString(480,current_row-380,saldo_restante)

	current_row=current_row-20
	current_row = 700
	p.setFont("Helvetica-Bold",7)
	p.drawString(55,440,"Nota: ")
	p.drawString(55,440-380,"Nota: ")
	p.setFont("Helvetica",7)
	p.drawString(75,440,"El artículo fue probado en sucursal junto con el cliente  y se aparta funcionando. Por ser un artículo usado no se da ningun tipo de garantia.  ")
	p.drawString(75,440-380,"El artículo fue probado en sucursal junto con el cliente y se aparta funcionando. Por ser un artículo usado no se da ningun tipo de garantia.  ")
	current_row=current_row-10
	#p.drawString(330,current_row,"y se aparta funcionando.")
	#p.drawString(330,current_row,"y se aparta funcionando.")
	current_row=current_row-10
	#p.drawString(330,current_row,"Por ser un artículo usado no se da ningun tipo de garantia. ")
	#p.drawString(330,current_row,"Por ser un artículo usado no se da ningun tipo de garantia. ")
	current_row=current_row-10
	p.drawString(330,current_row,"")
	p.drawString(330,current_row,"")
	

	current_row=530-20
	current_row=current_row-20
	
	p.line(50,current_row-380,250,current_row-380)
	p.line(50,current_row,250,current_row)

	current_row=current_row-20
	p.drawString(120,current_row-380,"Firma Cliente.")
	p.drawString(120,current_row,"Firma Valuador.")


	linea_corte=50

	pinta=0

	while linea_corte<600:
		if pinta==0:
			p.line(linea_corte,420,linea_corte-20,420)
			pinta=1
		else:
			
			pinta=0

		linea_corte=linea_corte+20


	p.showPage()#terminar pagina actual

	p.save()

	pdf=buffer.getvalue()

	buffer.close()

	response.write(pdf)
	Imprime_Apartado.objects.get(usuario=request.user).delete()
	return response


#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

@transaction.atomic
def venta_piso(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()


	if caja == None:
		caja_abierta="0"
		caja=Cajas

	suc  = user_2.sucursal


	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  


	suc  = user_2.sucursal

	username=request.user.username
	id_sucursal=user_2.sucursal.id

	est_Vendida=Estatus_Boleta.objects.get(id=6)

	error="0"
	ok = "0"
	if request.method=="POST":
		try:
		
			
			usuario=request.user
			
			#obtenemos todos los productos de la cotizacion del usuario
			vtp=Venta_Temporal_Piso.objects.filter(usuario=usuario)

			importe_mutuo=0.00
			importe_avaluo=0.00
			importe_total=0.00

			#obtenemos los totales para crear la venta.
			for v in vtp:
				importe_mutuo=decimal.Decimal(importe_mutuo)+decimal.Decimal(v.boleta.mutuo)
				importe_avaluo=decimal.Decimal(importe_avaluo)+decimal.Decimal(v.boleta.avaluo)
				importe_total=decimal.Decimal(importe_total) + v.boleta.fn_calcula_precio_venta()

			#es la clave para vENTA pISO.
			tm=Tipo_Movimiento.objects.get(id=6)
			#generamos el folio para la venta piso.
			folio=fn_folios(tm,suc)

			#creamos la venta piso.
			vp=Venta_Piso()
			vp.folio=folio
			vp.usuario=request.user
			vp.importe_mutuo=importe_mutuo
			vp.importe_avaluo=importe_avaluo
			vp.sucursal=suc
			vp.importe_venta=int(importe_total)
			vp.caja=caja
			vp.nombre_cliente = request.POST.get("nombre_cliente")
			vp.telefono = request.POST.get("telefono")
			vp.save()

			vtp=Venta_Temporal_Piso.objects.filter(usuario=usuario)

			for v in vtp:
				dvp=Det_Venta_Piso()
				dvp.venta = vp
				dvp.boleta = v.boleta
				dvp.importe_venta = v.boleta.fn_calcula_precio_venta()
				dvp.save()

				#cambiamos el estatus de la boleta a vendida.
				v.boleta.estatus=est_Vendida
				v.boleta.save()

			Venta_Temporal_Piso.objects.filter(usuario=usuario).delete()

			#como solo puede imprimirse una venta a la vez, se eliminan todas las que ya existan
			Imprime_Venta_Piso.objects.filter(usuario=request.user).delete()

			Imprime_Venta_Piso.objects.create(usuario=request.user,venta_piso=vp)

			ok = "1"
			id_venta = vp.id
			return render(request,'empenos/venta_piso.html',locals())
		except Exception as e:
			print(e)
			form=Venta_Piso_Form()
			error="1"
			return render(request,'empenos/venta_piso.html',locals())
	form=Venta_Piso_Form()
	return render(request,'empenos/venta_piso.html',locals())



def re_imprimir_venta_piso(request,id_venta):
	venta=Venta_Piso.objects.get(id=id_venta)
	Imprime_Venta_Piso.objects.filter(usuario=request.user).delete()
	Imprime_Venta_Piso.objects.create(usuario=request.user,venta_piso=venta)
	return imprime_venta_piso(request)



def imprime_venta_piso(request):
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename=hello.pdf'

	im=Imprime_Venta_Piso.objects.get(usuario=request.user)

	dv=Det_Venta_Piso.objects.filter(venta=im.venta_piso)

	cont_boletas=dv.count()#numero de boletas en la venta

	#cada 28 boletas salta de pagina
	reg_x_pag=28
	#obtenemos el numero de paginas
	num_paginas=math.ceil(cont_boletas/27)

	#obtenemos el abono a imprimir.
	#abono=Imprime_Abono.objects.get(usuario=request.user).abono
	buffer=BytesIO()

	p=canvas.Canvas(buffer,pagesize=A4)

	heigth_row=20#cada renglon es de 20.

	current_row=730

	p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg',40,750,100, 30)
	p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg',340,750,100, 30)

	p.drawString(400,790,"Copia cliente")

	p.setFont("Helvetica-Bold",10)

	p.drawString(170,760,"Folio venta: "+str(im.venta_piso.folio))
	p.drawString(470,760,"Folio venta: "+str(im.venta_piso.folio))

	p.setFont("Helvetica-Bold",12)
	p.drawString(100,current_row,"TICKET VENTA")
	p.drawString(400,current_row,"TICKET VENTA")

	current_row=current_row-20
	current_row=current_row-20
	p.setFont("Helvetica",10)



	

	p.drawString(35,current_row,"Fecha emisión: ")
	p.drawString(130,current_row,str(im.venta_piso.fecha.strftime("%Y-%m-%d")))
	p.drawString(335,current_row,"Fecha emisión: ")
	p.drawString(430,current_row,str(im.venta_piso.fecha.strftime("%Y-%m-%d")))

	current_row=current_row-20
	p.drawString(35,current_row,"Sucursal:")
	p.drawString(100,current_row,im.venta_piso.sucursal.sucursal)

	p.drawString(335,current_row,"Sucursal:")
	p.drawString(400,current_row,im.venta_piso.sucursal.sucursal)

	current_row=current_row-20
	p.setFont("Helvetica",10)
	p.drawString(35,current_row,"Cliente: ")
	p.setFont("Helvetica",7)
	p.drawString(100,current_row,im.venta_piso.cliente.nombre+' '+im.venta_piso.cliente.apellido_p+' '+im.venta_piso.cliente.apellido_m)
	p.setFont("Helvetica",10)
	p.drawString(335,current_row,"Cliente: ")
	p.setFont("Helvetica",7)
	p.drawString(400,current_row,im.venta_piso.cliente.nombre+' '+im.venta_piso.cliente.apellido_p+' '+im.venta_piso.cliente.apellido_m)
	p.setFont("Helvetica",10)
	current_row=current_row-20
	current_row=current_row-20

	p.setFont("Helvetica-Bold",10)
	p.drawString(35,current_row,"Artículo")
	p.drawString(230,current_row,"Precio")

	p.drawString(335,current_row,"Artículo")
	p.drawString(530,current_row,"Precio")

	p.setFont("Helvetica",7)
	current_row=current_row-20

	for d in dv:
		boleta=d.boleta
		dbe=Det_Boleto_Empeno.objects.filter(boleta_empeno=boleta)

		importe="$"+"{:0,.2f}".format(int(d.importe_venta))

		p.drawString(30,current_row,">")
		p.drawString(330,current_row,">")

		p.drawString(230,current_row,importe)
		p.drawString(530,current_row,importe)

		for db in dbe:
			p.drawString(35,current_row,"fb:"+str(db.boleta_empeno.folio)+"; "+db.descripcion)
			p.drawString(335,current_row,"fb:"+str(db.boleta_empeno.folio)+"; "+db.descripcion)

			current_row=current_row-20
			print("observaciones")
			print(db.observaciones)
			p.drawString(35,current_row,"Observaciones:"+db.observaciones)
			p.drawString(335,current_row,"Observaciones:"+db.observaciones)
			
			current_row=current_row-20

	p.setFont("Helvetica-Bold",10)	
	p.drawString(170,current_row,"Total: ")		
	p.drawString(470,current_row,"Total: ")		
	importe_venta="$"+"{:0,.2f}".format(int(im.venta_piso.importe_venta))	
	p.drawString(220,current_row,importe_venta)	
	p.drawString(520,current_row,importe_venta)	

	current_row=current_row-20

	p.setFont("Helvetica-Bold",7)
	p.drawString(40,current_row,"Nota: ")	
	p.drawString(340,current_row,"Nota: ")	
	p.setFont("Helvetica",7)
	p.drawString(70,current_row,"El artículo fue probado en sucursal junto con el cliente y se entrega ")	
	p.drawString(370,current_row,"El artículo fue probado en sucursal junto con el cliente y se entrega ")	
	current_row=current_row-10
	p.drawString(70,current_row,"funcionando.")	
	p.drawString(370,current_row,"funcionando.")	
	current_row=current_row-10
	p.drawString(70,current_row,"Por ser un artículo usado no se da ningun tipo de garantia.")	
	p.drawString(370,current_row,"Por ser un artículo usado no se da ningun tipo de garantia.")	
	current_row=current_row-10
	p.drawString(70,current_row,"")
	p.drawString(370,current_row,"")		
	

	current_row=current_row-20	
	current_row=current_row-20	
	
	p.line(50,current_row,250,current_row)
	p.line(350,current_row,550,current_row)

	current_row=current_row-20	
	p.drawString(120,current_row,"Firma Cliente.")		
	p.drawString(420,current_row,"Firma Cliente.")		

	

	linea_corte=800

	pinta=0

	while linea_corte>0:
		if pinta==0:
			p.line(300,linea_corte,300,linea_corte-20)		
			pinta=1
		else:
			
			pinta=0

		linea_corte=linea_corte-20
	

	p.showPage()#terminar pagina actual

	p.save()

	pdf=buffer.getvalue()

	buffer.close()

	response.write(pdf)
	Imprime_Venta_Piso.objects.get(usuario=request.user).delete()
	return response

	


#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

def cancela_boleta(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(15):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))
		
	user_2_virtual = User_2.objects.get(user = user_2.sucursal.usuario_virtual)

	caja = user_2_virtual.fn_tiene_caja_abierta()


	if caja == None:
		caja_abierta = "0"
		caja = Cajas()

	hoy = date.today()

	fecha_inicial = datetime.combine(hoy,time.min)
	fecha_final = datetime.combine(hoy,time.max)

	boletas = None
	if request.method == "POST":
		id_sucursal = request.POST.get("sucursal")

		sucursal = Sucursal.objects.get(id = int(id_sucursal))

		boletas = Boleta_Empeno.objects.filter(sucursal = sucursal,fecha__range = (fecha_inicial,fecha_final))

	form = Cancela_Boleta_Form()
	return render(request,'empenos/cancela_boleta.html',locals())

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

"""
idpermiso  =16
"""
def elimina_costo_extra(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(16):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))



	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	try:
		id_sucursal=int(request.POST.get("sucursal"))
		#validamos si el usuario tiene caja abierta en el dia actual.
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=request.user)
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja

	except Exception as e:
		print(e)
		caja_abierta="0"
		caja=Cajas

	
	permiso="1"



	if request.method=="POST":
		rce=Reg_Costos_Extra.objects.filter(fecha__range=(min_pub_date_time,max_pub_date_time))
	else:
		print("NA")
	form=Costo_Extra_Form()

	return render(request,'empenos/elimina_costo_extra.html',locals())


"""
idpermiso = 17
"""
def elimina_retiro (request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(17):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	try:
		#validamos si el usuario tiene caja abierta en el dia actual.
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=request.user)
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja
	except Exception as e:
		print(e)
		caja_abierta="0"
		caja=Cajas

	permiso="0"

	retiros = None
	id_usuario=user_2.user.id


	permiso="1"
		
	if request.method == "POST":

		id_sucursal = request.POST.get("sucursal")
		
		hoy = date.today()
		fecha_inicial = datetime.combine(hoy,time.min)
		fecha_final = datetime.combine(hoy,time.max)

		retiros = Retiro_Efectivo.objects.filter(sucursal__id = int(id_sucursal), fecha__range = (fecha_inicial,fecha_final), activo = 1)

	form = Elimina_Retiro_Form()
	return render(request,'empenos/elimina_retiro.html',locals())
#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
def forzar_desempeno(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(26):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	caja = user_2.fn_tiene_caja_abierta()

	if caja != None:
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja
	else:
		caja_abierta="0"
		caja=Cajas

	form = Establece_Costo_Desempeno()

	#mandamos el usuario para saber quien forzo el desempeño
	id_usuario = request.user.id

	return render(request,'empenos/forzar_desempeno.html',locals())
#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

def reporte_retiros_efectivo(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(22):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	caja = user_2.fn_tiene_caja_abierta()

	if caja != None:
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja
	else:
		caja_abierta="0"
		caja=Cajas
	leyenda = ""
	if request.method == "POST":

		id_sucursal = request.POST.get("sucursal")

		hoy = date.today()

		fecha_inicial = datetime.strptime(request.POST.get("fecha_inicial"),'%Y-%m-%d').date()
		fecha_final = datetime.strptime(request.POST.get("fecha_final"),'%Y-%m-%d').date()

		fecha_inicial = datetime.combine(fecha_inicial,time.min)
		fecha_final = datetime.combine(fecha_final,time.max)
		sucursal = Sucursal.objects.get(id = id_sucursal).sucursal
		leyenda = " de la sucursal " + sucursal + " del " + request.POST.get("fecha_inicial") + " al " +request.POST.get("fecha_final")
		retiros = Retiro_Efectivo.objects.filter(sucursal__id = int(id_sucursal), fecha__range = (fecha_inicial,fecha_final)).order_by("folio")
		if request.POST.get("export_pdf") == "1":
			
			return reporte_retiro_efectivo(retiros,request.POST.get("fecha_inicial"),request.POST.get("fecha_final"),request,sucursal)

	form = Reporte_Retiros_Form()

	return render(request,'empenos/reporte_retiros_efectivo.html',locals())

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
def reporte_ingresos_efectivo(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(23):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	caja = user_2.fn_tiene_caja_abierta()

	if caja != None:
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja
	else:
		caja_abierta="0"
		caja=Cajas

	leyenda = ""
	if request.method == "POST":

		id_sucursal = request.POST.get("sucursal")

		hoy = date.today()

		fecha_inicial = datetime.strptime(request.POST.get("fecha_inicial"),'%Y-%m-%d').date()
		fecha_final = datetime.strptime(request.POST.get("fecha_final"),'%Y-%m-%d').date()

		fecha_inicial = datetime.combine(fecha_inicial,time.min)
		fecha_final = datetime.combine(fecha_final,time.max)
		sucursal = Sucursal.objects.get(id = id_sucursal).sucursal

		leyenda = " de la sucursal " + sucursal + " del " + request.POST.get("fecha_inicial") + " al " +request.POST.get("fecha_final")

		ingresos = Otros_Ingresos.objects.filter(sucursal__id = int(id_sucursal), fecha__range = (fecha_inicial,fecha_final)).order_by("folio")

		if request.POST.get("export_pdf") == "1":
			return rep_ingresos_efectivo(ingresos,request.POST.get("fecha_inicial"),request.POST.get("fecha_final"),request,sucursal)

	form = Reporte_Retiros_Form()

	return render(request,'empenos/reporte_ingreso_efectivo.html',locals())
#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

def reporte_boletas(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2_1.fn_tiene_acceso_a_vista(25):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	caja = user_2.fn_tiene_caja_abierta()

	c = ""

	if caja != None:
		c = caja.caja
	
	if request.method == "POST":
		id_sucursal = request.POST.get("sucursal")
		id_estatus = request.POST.get("estatus")
		if id_estatus == "":
			boletas = Boleta_Empeno.objects.filter(sucursal__id = int(id_sucursal)).order_by("-folio")	
		else:
			boletas = Boleta_Empeno.objects.filter(sucursal__id = int(id_sucursal),estatus__id = int(id_estatus)).order_by("-folio")	
		leyenda = "de la sucursal " + Sucursal.objects.get(id = int(id_sucursal)).sucursal 

		if id_estatus == "":
			leyenda = "de todos los estatus de la sucursal " + Sucursal.objects.get(id = int(id_sucursal)).sucursal  
		else:
			leyenda = "del estatus " + Estatus_Boleta.objects.get(id = int(id_estatus)).estatus + " de la sucursal " + Sucursal.objects.get(id = int(id_sucursal)).sucursal 

		if request.POST.get("export_pdf") == "1":
			return rep_boleta_empeno(boletas,leyenda,request)

		if request.POST.get("export_pdf") == "3":
			try:
				estatus = Estatus_Boleta.objects.get(id=id_estatus)
				return reporte_boletas_excel(boletas,estatus.estatus)
			except:
				return reporte_boletas_excel(boletas,"Todos")

			

	form = Reporte_Boletas_Form()

	return render(request,'empenos/reporte_boletas.html',locals())

def reporte_boletas_excel(boletas,estatus):


			try:
				if estatus == "Todos":
					nom_archivo='Rep_Boletas.csv'
				else:
					nom_archivo='Rep_Boletas_en_' + estatus + '.csv'

				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="'+nom_archivo+'"'

				writer = csv.writer(response)
				writer.writerow(['Folio','Sucursal','Fecha Emision','Nombre Usuario','Usuario','Cliente','Teléfono fijo','Teléono celular','Avaluo','Mutuo','Estatus','Fecha Vencimiento','Tipo Producto','Descripción Producto (s)'])

				for b in boletas:
					d_boleta = Det_Boleto_Empeno.objects.filter(boleta_empeno = b)					
					descripcion = ""
					for db in d_boleta:
						descripcion = descripcion + 'Descripción ' +  db.descripcion 

						if db.costo_kilataje != None:
							descripcion = descripcion  + ', Kilataje: ' + db.costo_kilataje.kilataje
							descripcion = descripcion  + ', Peso: ' + str(db.peso)
						
						descripcion = descripcion + '; '

					writer.writerow([b.folio,b.sucursal.sucursal,b.fecha.strftime('%Y-%m-%d'),b.usuario.username,b.usuario.first_name+' '+b.usuario.last_name,b.cliente.nombre+' '+b.cliente.apellido_p+' '+b.cliente.apellido_m,b.cliente.telefono_fijo,b.cliente.telefono_celular,b.avaluo,b.mutuo,b.estatus.estatus,b.fecha_vencimiento.strftime('%Y-%m-%d'),b.tipo_producto.tipo_producto,descripcion])
				
			except:
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="'+nom_archivo+'"'

				writer = csv.writer(response)
				writer.writerow(['Folio','Sucursal','Fecha Emision','Nombre Usuario','Usuario','Cliente','Avaluo','Mutuo','Estatus','Fecha Vencimiento','Tipo Producto','Descripción Producto (s)'])
			return response


				
#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

def reporte_cajas_abiertas(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(21):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	caja = user_2.fn_tiene_caja_abierta()

	if caja != None:
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja
	else:
		caja_abierta="0"
		caja=Cajas

	leyenda = ""
	if request.method == "POST":

		id_sucursal = request.POST.get("sucursal")

		hoy = date.today()

		fecha_inicial = datetime.strptime(request.POST.get("fecha_inicial"),'%Y-%m-%d').date()
		fecha_final = datetime.strptime(request.POST.get("fecha_final"),'%Y-%m-%d').date()

		fecha_inicial = datetime.combine(fecha_inicial,time.min)
		fecha_final = datetime.combine(fecha_final,time.max)
		sucursal = Sucursal.objects.get(id = id_sucursal)

		txt_sucursal = Sucursal.objects.get(id = id_sucursal).sucursal
		leyenda = " de la sucursal " + txt_sucursal + " del " + request.POST.get("fecha_inicial") + " al " +request.POST.get("fecha_final")

		cajas = Cajas.objects.filter(sucursal = sucursal,fecha__range = (fecha_inicial,fecha_final)).order_by("-fecha")

		if request.POST.get("export_pdf") == "1":
			return rep_cajas_abiertas(cajas,request.POST.get("fecha_inicial"),request.POST.get("fecha_final"),request,txt_sucursal)


	form = Reporte_Cajas_Form()

	return render(request,'empenos/reporte_cajas_abiertas.html',locals())
#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

def consulta_apartado(request):
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

	if caja == None:
		caja_abierta="0"
		caja=Cajas
	else:
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja

	permiso="1"	

	estatus_apartado = Estatus_Apartado.objects.all()
	if request.method=="POST":

		folio_apartado = request.POST.get("folio_apartado")

		if request.POST.get("fecha_inicial") != "" and request.POST.get("fecha_inicial") != None : 
			fecha_inicial = request.POST.get("fecha_inicial")
			fecha_final = request.POST.get("fecha_final")


			fecha_inicial = datetime.strptime(fecha_inicial,'%Y-%m-%d').date()
			fecha_final = datetime.strptime(fecha_final,'%Y-%m-%d').date()

			fecha_inicial = datetime.combine(fecha_inicial,time.min)
			fecha_final = datetime.combine(fecha_final,time.max)

			apartados = Apartado.objects.filter(fecha__range = (fecha_inicial,fecha_final),sucursal = suc).order_by("-folio")
		elif request.POST.get("cliente") != "" and request.POST.get("cliente") != None:			
			
			cl = Cliente.objects.filter(nombre_completo__contains = request.POST.get("cliente").upper()) 

			if request.POST.get("estatus_apartado") != None and request.POST.get("estatus_apartado") != "":
				estatus = Estatus_Apartado.objects.get(id = int(request.POST.get("estatus_apartado")))	
				apartados = (Apartado.objects.filter(cliente__in = cl,sucursal = suc,estatus = estatus) | Apartado.objects.filter(nombre_cliente__icontains = request.POST.get("cliente").upper(),sucursal = suc,estatus = estatus) )
			else:
				apartados = (Apartado.objects.filter(cliente__in = cl,sucursal = suc) | Apartado.objects.filter(nombre_cliente__icontains = request.POST.get("cliente").upper(),sucursal = suc) )

		elif folio_apartado != "" or folio_apartado != None :
			apartados = Apartado.objects.filter(folio = int(request.POST.get("folio_apartado")),sucursal = suc)

		form=Buscar_Apartados_Form(request.POST)
	else:
		form=Buscar_Apartados_Form()

	return render(request,'empenos/consulta_apartado.html',locals())

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
def consulta_venta(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()


	if caja == None:
		caja_abierta="0"
		caja=Cajas
		return render(request,'empenos/consulta_venta.html',locals())

	
	suc=caja.sucursal
	c=caja.caja
	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	
		
	permiso="1"	

	if request.method=="POST":		
		fecha_inicial=datetime.strptime(request.POST.get("fecha_inicial"),"%Y-%m-%d").date()
		fecha_final=datetime.strptime(request.POST.get("fecha_final"),"%Y-%m-%d").date()

		fecha_inicial=datetime.combine(fecha_inicial,time.min)
		fecha_final=datetime.combine(fecha_final,time.max)

		vg=Venta_Granel.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=suc).order_by("id")

		vp=Venta_Piso.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=suc).order_by("id")

	else:
		form=Buscar_Ventas_Form()
	
	return render(request,'empenos/consulta_venta.html',locals())
#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
@transaction.atomic
def venta_granel(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()


	if caja == None:
		caja_abierta="0"
		caja=Cajas
		return render(request,'empenos/venta_granel.html',locals())

	suc  = user_2.sucursal

	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	permiso="1"	

	error="0"#no muestra error
	#validamos tambien el permiso al hacer post, por si modificaron el front para tener acceso a la pantalla
	if request.method=="POST" and permiso=="1":
		try:
			error="1"#todo bien
			#obtenemos todas las boletas que estan marcadas para venta.
			vt2=Venta_Temporal.objects.filter(usuario=user_2.user,vender="S")
			#en caso de que no se haya seleccionado al menos una boleta para la venta, 
			#se regresa error al guardar
			if not vt2.exists():
				error="2"
				return render(request,'empenos/venta_granel.html',locals())

			avaluo=0.00
			mutuo=0.00

			for x in vt2:
				avaluo=decimal.Decimal(avaluo)+decimal.Decimal(x.boleta.avaluo)
				mutuo=decimal.Decimal(mutuo)+decimal.Decimal(x.boleta.mutuo)
			
			#la caja y el importe de venta se muestra hasta que se le da entrada al dinero.
			vg=Venta_Granel()
			vg.usuario=request.user
			vg.importe_mutuo=mutuo
			vg.importe_avaluo=avaluo
			vg.sucursal=user_2.sucursal
			vg.save()

			#obtenemos todas las boletas que estan marcadas para venta.
			vt2=Venta_Temporal.objects.filter(usuario=user_2.user,vender="S")
			
			#estatus vendida
			vendida=Estatus_Boleta.objects.get(id=6)

			for x in vt2:
				dvg = Det_Venta_Granel()
				dvg.boleta = x.boleta
				dvg.venta = vg
				dvg.save()	

				#todas las boletas que se incluyan el na venta, se marcara como boleta vendida.
				x.boleta.estatus=vendida
				x.boleta.save()					

			#borramos las boletas que el usuario imprimio anterior mente, en caso de existir
			Imprime_Venta_Granel.objects.filter(usuario=request.user).delete()

			#almacenamos la venta en la tabla para imprimir.
			Imprime_Venta_Granel.objects.create(usuario=request.user,venta_granel=vg)

			#borramos la venta temporal
			Venta_Temporal.objects.filter(usuario=user_2.user).delete()

			error="3"
			return imprime_venta_granel(request)
		except Exception as e:
			error="2"#indica que fallo al guardar y debera mostrar un mensaje de error en pantalla.
			print(e)
	else:		
		#buscamos los estatus remate y almoneda.
		boletas=(Boleta_Empeno.objects.filter(estatus=5,sucursal=user_2.sucursal) | Boleta_Empeno.objects.filter(estatus=3,sucursal=user_2.sucursal)).exclude(tipo_producto=3)

		#borramos todas las ventas temporales del usuario
		vt=Venta_Temporal.objects.filter(usuario=user_2.user).delete()

		
		for b in boletas:
			Venta_Temporal.objects.create(usuario=user_2.user,boleta=b,fecha=min_pub_date_time)
		vt=Venta_Temporal.objects.filter(usuario=user_2.user)
	return render(request,'empenos/venta_granel.html',locals())

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
"""
idpermiso = 9
"""
def admin_kilataje(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(9):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))


	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	try:
		#validamos si el usuario tiene caja abierta en el dia actual.
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=request.user)
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja
	except Exception as e:
		print(e)
		caja_abierta="0"
		caja=Cajas

	permiso="1"		

	cat_kilataje=Costo_Kilataje.objects.filter(activo="S").order_by("kilataje")
	cat_tipo_kilataje=Tipo_Kilataje.objects.all()
	cat_tipo_producto=Tipo_Producto.objects.filter().exclude(id=3)
	return render(request,'empenos/admin_kilataje.html',locals())


#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
def otros_ingresos(request):
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
	caja_abierta="0"
	if caja != None:
		c=caja.caja
		caja_abierta="1"
		suc = caja.sucursal


	exito="0"
	id_ingreso = "0"
	if request.method=="POST":
		form=Otros_Ingresos_Form(request.POST)

		#es la clave para otros ingresos.
		tm=Tipo_Movimiento.objects.get(id=2)
		folio=fn_folios(tm,suc)
		str_folio=fn_str_clave(folio)

		if form.is_valid():
			f=form.save(commit=False)
			f.sucursal=suc
			f.folio=str_folio
			f.usuario=request.user
			f.caja=c
			f.ocaja = caja
			f.save()
			id_ingreso = f.id
			#return HttpResponseRedirect(reverse('seguridad:admin_cajas'))
			exito="1"
			form=Otros_Ingresos_Form()
	else:
		form=Otros_Ingresos_Form()
	return render(request,'empenos/otros_ingresos.html',locals())

"""
idpermiso = 19
"""
def rep_comparativo_estatus_cartera(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
	
	print(user_2.fn_tiene_acceso_a_vista(19))
	if not user_2.fn_tiene_acceso_a_vista(19):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))


	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	c = ""
	if caja != None:
		c=caja.caja
	
	msj_error = ""

	#el estatus 1 indica que todo esta ok, 
	#el estatus 0 indica que se presento un error. el error debe venir acompalñado de una leyenda en la variable msj_error
	estatus = "1" 

	sucursales = Sucursal.objects.all()

	txt_sucursal = ""

	if request.method == "POST":
		#si contiene 0 es que no se exporta
		#si contiene 1 es que se exporta
		export_pdf = request.POST.get("export_pdf")

		
		id_sucursal = request.POST.get("sucursal")

		fecha_inicial= datetime.strptime(request.POST.get("fecha_inicial"), "%Y-%m-%d").date()
		fecha_final = datetime.strptime(request.POST.get("fecha_final"),"%Y-%m-%d").date()

		fecha_inicial = datetime.combine(fecha_inicial,time.min)
		fecha_final = datetime.combine(fecha_final,time.min)

		cont_activas_1 = 0
		mutuo_activo_1 = 0.00
		avaluo_activo_1 = 0.00

		cont_almoneda_1 = 0
		mutuo_almoneda_1 = 0.00
		avaluo_almoneda_1 = 0.00


		cont_remate_1 = 0
		mutuo_remate_1 = 0.00
		avaluo_remate_1 = 0.00

		cont_activas_2 = 0
		mutuo_activo_2 = 0.00
		avaluo_activo_2 = 0.00

		cont_almoneda_2 = 0
		mutuo_almoneda_2 = 0.00
		avaluo_almoneda_2 = 0.00


		cont_remate_2 = 0
		mutuo_remate_2 = 0.00
		avaluo_remate_2 = 0.00


		if fecha_inicial >= fecha_final:
			estatus = "2"
			msj_error = "La fecha 2 debe ser mayor a la fecha 1."
			return render(request,'empenos/rep_comparativo_estatus_cartera.html',locals())	

		if fecha_final == datetime.combine(date.today(),time.min):
			estatus = "2"
			msj_error = "No puede seleccionar el dia de hoy para comparar."
			return render(request,'empenos/rep_comparativo_estatus_cartera.html',locals())				

		if id_sucursal != "":

			sucursal = Sucursal.objects.get(id = int(id_sucursal))

			txt_sucursal = sucursal.sucursal

			try:
				cartera_1 = Historico_Estatus_Cartera.objects.get(fecha = fecha_inicial,sucursal = sucursal) 			

			except Exception as e:				
				print(e)
				estatus = "2"
				msj_error = "La fecha 1 no cuenta información."
				return render(request,'empenos/rep_comparativo_estatus_cartera.html',locals())	

			try:
				cartera_2 = Historico_Estatus_Cartera.objects.get(fecha = fecha_final,sucursal = sucursal) 
			except Exception as e:
				cartera_1 = None
				print(e)
				estatus = "2"
				msj_error = "La fecha 2 no cuenta información."
				return render(request,'empenos/rep_comparativo_estatus_cartera.html',locals())	
			cont_activas_1 = cartera_1.num_boletas_activas
			mutuo_activo_1 = cartera_1.importe_mutuo_activas
			avaluo_activo_1 = cartera_1.importe_avaluo_activas

			cont_almoneda_1 = cartera_1.num_boletas_almoneda
			mutuo_almoneda_1 = cartera_1.importe_mutuo_almoneda
			avaluo_almoneda_1 = cartera_1.importe_avaluo_almoneda

			cont_remate_1 = cartera_1.num_boletas_remate
			mutuo_remate_1 = cartera_1.importe_mutuo_remate
			avaluo_remate_1 = cartera_1.importe_avaluo_remate

			cont_total_1 = cont_activas_1 + cont_almoneda_1 + cont_remate_1
			total_mutuo_1 = mutuo_activo_1 + mutuo_almoneda_1 + mutuo_remate_1
			total_avaluo_1 = avaluo_activo_1 + avaluo_almoneda_1 + avaluo_remate_1

			cont_activas_2 = cartera_2.num_boletas_activas
			mutuo_activo_2 = cartera_2.importe_mutuo_activas
			avaluo_activo_2 = cartera_2.importe_avaluo_activas

			cont_almoneda_2 = cartera_2.num_boletas_almoneda
			mutuo_almoneda_2 = cartera_2.importe_mutuo_almoneda
			avaluo_almoneda_2 = cartera_2.importe_avaluo_almoneda

			cont_remate_2 = cartera_2.num_boletas_remate
			mutuo_remate_2 = cartera_2.importe_mutuo_remate
			avaluo_remate_2 = cartera_2.importe_avaluo_remate

		else:#comparamos todas las sucursales.
			resp_fecha_1 = Historico_Estatus_Cartera.objects.filter(fecha = fecha_inicial)
			resp_fecha_2 = Historico_Estatus_Cartera.objects.filter(fecha = fecha_final)

			if not resp_fecha_1.exists():
				estatus = "2"
				msj_error = "La fecha 1 no cuenta información."
				return render(request,'empenos/rep_comparativo_estatus_cartera.html',locals())	

			if not resp_fecha_2.exists():
				estatus = "2"
				msj_error = "La fecha 2 no cuenta información."
				return render(request,'empenos/rep_comparativo_estatus_cartera.html',locals())	

			txt_sucursal = "Todas"

			cont_activas_1 = resp_fecha_1.aggregate(Sum("num_boletas_activas"))["num_boletas_activas__sum"]
			mutuo_activo_1 = resp_fecha_1.aggregate(Sum("importe_mutuo_activas"))["importe_mutuo_activas__sum"]
			avaluo_activo_1 = resp_fecha_1.aggregate(Sum("importe_avaluo_activas"))["importe_avaluo_activas__sum"]

			cont_almoneda_1 = resp_fecha_1.aggregate(Sum("num_boletas_almoneda"))["num_boletas_almoneda__sum"]
			mutuo_almoneda_1 = resp_fecha_1.aggregate(Sum("importe_mutuo_almoneda"))["importe_mutuo_almoneda__sum"]
			avaluo_almoneda_1 = resp_fecha_1.aggregate(Sum("importe_avaluo_almoneda"))["importe_avaluo_almoneda__sum"]

			cont_remate_1 = resp_fecha_1.aggregate(Sum("num_boletas_remate"))["num_boletas_remate__sum"]
			mutuo_remate_1 = resp_fecha_1.aggregate(Sum("importe_mutuo_remate"))["importe_mutuo_remate__sum"]
			avaluo_remate_1 = resp_fecha_1.aggregate(Sum("importe_avaluo_remate"))["importe_avaluo_remate__sum"]


			cont_activas_2 = resp_fecha_2.aggregate(Sum("num_boletas_activas"))["num_boletas_activas__sum"]
			mutuo_activo_2 = resp_fecha_2.aggregate(Sum("importe_mutuo_activas"))["importe_mutuo_activas__sum"]
			avaluo_activo_2 = resp_fecha_2.aggregate(Sum("importe_avaluo_activas"))["importe_avaluo_activas__sum"]

			cont_almoneda_2 = resp_fecha_2.aggregate(Sum("num_boletas_almoneda"))["num_boletas_almoneda__sum"]
			mutuo_almoneda_2 = resp_fecha_2.aggregate(Sum("importe_mutuo_almoneda"))["importe_mutuo_almoneda__sum"]
			avaluo_almoneda_2 = resp_fecha_2.aggregate(Sum("importe_avaluo_almoneda"))["importe_avaluo_almoneda__sum"]

			cont_remate_2 = resp_fecha_2.aggregate(Sum("num_boletas_remate"))["num_boletas_remate__sum"]
			mutuo_remate_2 = resp_fecha_2.aggregate(Sum("importe_mutuo_remate"))["importe_mutuo_remate__sum"]
			avaluo_remate_2 = resp_fecha_2.aggregate(Sum("importe_avaluo_remate"))["importe_avaluo_remate__sum"]


		cont_total_1 = cont_activas_1 + cont_almoneda_1 + cont_remate_1
		total_mutuo_1 = mutuo_activo_1 + mutuo_almoneda_1 + mutuo_remate_1
		total_avaluo_1 = avaluo_activo_1 + avaluo_almoneda_1 + avaluo_remate_1

		cont_total_2 = cont_activas_2 + cont_almoneda_2 + cont_remate_2
		total_mutuo_2 = mutuo_activo_2 + mutuo_almoneda_2 + mutuo_remate_2
		total_avaluo_2 = avaluo_activo_2 + avaluo_almoneda_2 + avaluo_remate_2


		cont_activas_c = cont_activas_2 - cont_activas_1
		mutuo_activo_c = mutuo_activo_2 - mutuo_activo_1
		avaluo_activo_c = avaluo_activo_2 - avaluo_activo_1

		cont_almoneda_c = cont_almoneda_2 - cont_almoneda_1
		mutuo_almoneda_c = mutuo_almoneda_2 - mutuo_almoneda_1
		avaluo_almoneda_c = avaluo_almoneda_2 - avaluo_almoneda_1

		cont_remate_c = cont_remate_2 - cont_remate_1
		mutuo_remate_c = mutuo_remate_2 - mutuo_remate_1
		avaluo_remate_c = avaluo_remate_2 - avaluo_remate_1


	



		cont_total_c = cont_total_2 - cont_total_1
		total_mutuo_c = total_mutuo_2 - total_mutuo_1
		total_avaluo_c = total_avaluo_2 - total_avaluo_1

		mutuo_activo_c = "{:0,.2f}".format(mutuo_activo_c)
		avaluo_activo_c = "{:0,.2f}".format(avaluo_activo_c)
		mutuo_almoneda_c = "{:0,.2f}".format(mutuo_almoneda_c)
		avaluo_almoneda_c = "{:0,.2f}".format(avaluo_almoneda_c)
		avaluo_remate_c = "{:0,.2f}".format(avaluo_remate_c)
		mutuo_remate_c = "{:0,.2f}".format(mutuo_remate_c)
		total_mutuo_c = "{:0,.2f}".format(total_mutuo_c)
		total_avaluo_c = "{:0,.2f}".format(total_avaluo_c)


		mutuo_activo_1 =  "{:0,.2f}".format(mutuo_activo_1)
		avaluo_activo_1 = "{:0,.2f}".format(avaluo_activo_1)
		
		mutuo_almoneda_1 =  "{:0,.2f}".format(mutuo_almoneda_1)
		avaluo_almoneda_1 = "{:0,.2f}".format(avaluo_almoneda_1)

		mutuo_remate_1 =  "{:0,.2f}".format(mutuo_remate_1)
		avaluo_remate_1 = "{:0,.2f}".format(avaluo_remate_1)

		total_mutuo_1 =  "{:0,.2f}".format(total_mutuo_1)
		total_avaluo_1 = "{:0,.2f}".format(total_avaluo_1)



		mutuo_activo_2 =  "{:0,.2f}".format(mutuo_activo_2)
		avaluo_activo_2 = "{:0,.2f}".format(avaluo_activo_2)
		
		mutuo_almoneda_2 =  "{:0,.2f}".format(mutuo_almoneda_2)
		avaluo_almoneda_2 = "{:0,.2f}".format(avaluo_almoneda_2)

		mutuo_remate_2 =  "{:0,.2f}".format(mutuo_remate_2)
		avaluo_remate_2 = "{:0,.2f}".format(avaluo_remate_2)

		total_mutuo_2 =  "{:0,.2f}".format(total_mutuo_2)
		total_avaluo_2 = "{:0,.2f}".format(total_avaluo_2)


		txt_fecha_inicial = fecha_inicial.strftime("%Y-%m-%d")
		txt_fecha_final = fecha_final.strftime("%Y-%m-%d")
		if export_pdf == "1":
			dic_fecha_1 = {"cont_activas":str(cont_activas_1),"cont_almoneda":str(cont_almoneda_1),"cont_remate":str(cont_remate_1),"mutuo_activo":mutuo_activo_1,"mutuo_almoneda":mutuo_almoneda_1,"mutuo_remate":mutuo_remate_1,"avaluo_activo":avaluo_activo_1,"avaluo_almoneda":avaluo_almoneda_1,"avaluo_remate":avaluo_remate_1,"cont_total":str(cont_total_1),"mutuo_total":total_mutuo_1,"avaluo_total":total_avaluo_1}
			dic_fecha_2 = {"cont_activas":str(cont_activas_2),"cont_almoneda":str(cont_almoneda_2),"cont_remate":str(cont_remate_2),"mutuo_activo":mutuo_activo_2,"mutuo_almoneda":mutuo_almoneda_2,"mutuo_remate":mutuo_remate_2,"avaluo_activo":avaluo_activo_2,"avaluo_almoneda":avaluo_almoneda_2,"avaluo_remate":avaluo_remate_2,"cont_total":str(cont_total_2),"mutuo_total":total_mutuo_2,"avaluo_total":total_avaluo_2}
			dic_comparacion = {"cont_activas":str(cont_activas_c),"cont_almoneda":str(cont_almoneda_c),"cont_remate":str(cont_remate_c),"mutuo_activo":mutuo_activo_c,"mutuo_almoneda":mutuo_almoneda_c,"mutuo_remate":mutuo_remate_c,"avaluo_activo":avaluo_activo_c,"avaluo_almoneda":avaluo_almoneda_c,"avaluo_remate":avaluo_remate_c,"cont_total":str(cont_total_c),"mutuo_total":total_mutuo_c,"avaluo_total":total_avaluo_c}
			dic = { "fecha_1" : dic_fecha_1 , "fecha_2" : dic_fecha_2,"comparacion" : dic_comparacion }
			return reporte_comparativo_carteras(dic,user_2.user,txt_fecha_inicial,txt_fecha_final,txt_sucursal)
	else:
		form  = Comp_Carteras_Form()

	return render(request,'empenos/rep_comparativo_estatus_cartera.html',locals())
	
def rep_flujo_caja(request):

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

	c=""
	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  	

	msj_error=""	

	try:
		costo_reimpresion=Costo_Extra.objects.get(id=1).costo
	except:
		costo_reimpresion=0


	try:
		#validamos si el usuaario tiene caja abierta para mostrarla en el encabezado.
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=request.user)
		c=caja.caja
		id_caja=caja.id

	except Exception as e:
		msj_error="No cuentas con caja abierta."
		print(e)



	error=""#en caso de error en esta variable se manda el mensaje de error.
	est_error="0"#si es cero es que todo esta correcto.

	#obtenemos los el dia incial y final del mes actual
	today= datetime.now()
	dia_ultimo_mes = datetime.strptime(fn_last_day_of_month(today,2),'%Y-%m-%d')
	dia_primero_mes = datetime.strptime(fn_last_day_of_month(today,1),'%Y-%m-%d')

	


	post="0"

	cont_desempenos=0
	importe_desempenos=0.00

	importe_capital=0.00
	cont_capital=0

	importe_refrendo=0.00
	cont_refrendos=0

	importe_com_pg=0.00
	cont_com_pg=0

	cont_empenos=0
	importe_empenos=0.00
	saldo_inicial=0.00

	cont_otros=0
	importe_otros=0.00

	cont_activas=0
	mutuo_activo=0.00
	avaluo_activo=0.00


	cont_almoneda=0
	mutuo_almoneda=0.00
	avaluo_almoneda=0.00
	importe_retiros=0.00			
	cont_retiros=0


	cont_remate=0
	mutuo_remate=0.00
	avaluo_remate=0.00

	cont_ventas=0
	importe_ventas=0.00


	importe_venta_piso=0.00
	importe_avaluo_piso=0.00
	importe_mutuo_piso=0.00

	importe_reimpresion_boleta = 0.00
	cont_reimpresion_boleta = 0

	cont_venta_piso=0

	importe_venta_granel=0.00
	importe_avaluo_granel=0.00
	importe_mutuo_granel=0.00
	cont_venta_granel=0

	cont_ab_apartado=0
	importe_ab_apartado=0.00

	refrendo_aux = 0.00
	cpg_aux = 0.00
	ce_aux = 0.00
	ganancia_ventas_aux = 0.00
	im_retiros_aux = 0.00


	cont_t_entradas = 0
	importe_t_entradas = 0.00

	cont_t_salidas = 0
	importe_t_salidas = 0.00

	if request.method=="POST":

		post="1"

		est_activa=Estatus_Boleta.objects.get(id=1)
		est_almoneda=Estatus_Boleta.objects.get(id=3)
		est_remate=Estatus_Boleta.objects.get(id=5)

		sucursal=request.POST.get("sucursal")

		fecha_inicial= datetime.strptime(request.POST.get("fecha_inicial"), "%Y-%m-%d").date()
		fecha_final= datetime.strptime(request.POST.get("fecha_final"), "%Y-%m-%d").date()


		fec_inicial_caja=datetime.combine(fecha_inicial, time.min) 
		fec_final_caja=datetime.combine(fecha_inicial, time.max) 
			
		fecha_inicial=datetime.combine(fecha_inicial,time.min)
		fecha_final=datetime.combine(fecha_final,time.max)



		#si indicamos la sucursal
		if request.POST.get("sucursal")!="":
			sucursal=Sucursal.objects.get(id=sucursal)
			txt_sucursal=sucursal.sucursal

			refrendo_aux = sucursal.fn_get_total_refrendos(dia_primero_mes,dia_ultimo_mes)
			cpg_aux = sucursal.fn_get_total_comision_pg(dia_primero_mes,dia_ultimo_mes)
			ce_aux = sucursal.fn_get_total_costos_extras(dia_primero_mes,dia_ultimo_mes)			
			ganancia_ventas_aux = sucursal.fn_get_ganancia_ventas(dia_primero_mes,dia_ultimo_mes)
			im_retiros_aux = sucursal.fn_get_retiros(dia_primero_mes,dia_ultimo_mes)


			cont_ab_apartado = Abono_Apartado.objects.filter(fecha__range = (fecha_inicial,fecha_final),caja__sucursal = sucursal).count()

			iap = Abono_Apartado.objects.filter(fecha__range = (fecha_inicial,fecha_final),caja__sucursal = sucursal).aggregate(Sum("importe"))

			if iap["importe__sum"] != None:
				importe_ab_apartado = iap["importe__sum"]

			#buscamos ingresos por ventas
			cont_ventas=Venta_Granel.objects.filter(fecha_importe_venta__range=(fecha_inicial,fecha_final),sucursal=sucursal).count()
			imp_venta=Venta_Granel.objects.filter(fecha_importe_venta__range=(fecha_inicial,fecha_final),sucursal=sucursal).aggregate(Sum("importe_venta"))

			importe_ventas=0	
			if imp_venta["importe_venta__sum"]==None:
				importe_ventas=0.00
			else:
				importe_ventas=imp_venta["importe_venta__sum"]

			#buscamos ingresos por ventas piso
			cont_ventas=cont_ventas+Venta_Piso.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=sucursal).count()

			imp_venta=Venta_Piso.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=sucursal).aggregate(Sum("importe_venta"))	
			if imp_venta["importe_venta__sum"]==None:
				print("")
			else:
				importe_ventas=decimal.Decimal(importe_ventas)+decimal.Decimal(imp_venta["importe_venta__sum"])

			#calculamos el resumen de la venta piso
			cont_venta_piso=Venta_Piso.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=sucursal).count()
			imp_venta=Venta_Piso.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=sucursal).aggregate(Sum("importe_venta"))	
			imp_av_vp=Venta_Piso.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=sucursal).aggregate(Sum("importe_avaluo"))	
			imp_mut_vp=Venta_Piso.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=sucursal).aggregate(Sum("importe_mutuo"))	

			if imp_venta["importe_venta__sum"]==None:
				print("")
			else:
				importe_venta_piso=decimal.Decimal(imp_venta["importe_venta__sum"])

			if imp_av_vp["importe_avaluo__sum"]==None:
				print("")
			else:
				importe_avaluo_piso=decimal.Decimal(imp_av_vp["importe_avaluo__sum"])

			if imp_mut_vp["importe_mutuo__sum"]==None:
				print("")
			else:
				importe_mutuo_piso=decimal.Decimal(imp_mut_vp["importe_mutuo__sum"])




			#calculamos el resumen de la venta piso
			cont_venta_granel=Venta_Granel.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=sucursal).count()
			imp_venta=Venta_Granel.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=sucursal).aggregate(Sum("importe_venta"))	
			imp_av_vg=Venta_Granel.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=sucursal).aggregate(Sum("importe_avaluo"))	
			imp_mut_vg=Venta_Granel.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=sucursal).aggregate(Sum("importe_mutuo"))	

			if imp_venta["importe_venta__sum"]==None:
				print("")
			else:
				importe_venta_granel=decimal.Decimal(imp_venta["importe_venta__sum"])

			if imp_av_vg["importe_avaluo__sum"]==None:
				print("")
			else:
				importe_avaluo_granel=decimal.Decimal(imp_av_vg["importe_avaluo__sum"])

			if imp_mut_vg["importe_mutuo__sum"]==None:
				print("")
			else:
				importe_mutuo_granel=decimal.Decimal(imp_mut_vg["importe_mutuo__sum"])


			try:

				cajas_dia_inicial=Cajas.objects.filter(fecha__range=(fec_inicial_caja,fec_final_caja),sucursal=sucursal).aggregate(Sum("importe"))
				saldo_inicial=0.00

				if cajas_dia_inicial["importe__sum"]!=None:
					saldo_inicial=cajas_dia_inicial["importe__sum"]

			except Exception as e:
				print(e)
				error="Error al consultar el fondo incial"
				est_error="1"
				saldo_inicial=0.00	




			#calculamos los empeños
			importe_empenos=Boleta_Empeno.objects.filter(sucursal=sucursal,fecha__range=(fecha_inicial,fecha_final)).aggregate(Sum("mutuo_original"))
			cont_empenos=Boleta_Empeno.objects.filter(sucursal=sucursal,fecha__range=(fecha_inicial,fecha_final)).exclude(estatus__id = 2).count()

			if importe_empenos["mutuo_original__sum"]==None:
				importe_empenos=0.00
			else:
				importe_empenos=importe_empenos["mutuo_original__sum"]

			#obtenemos los costos extras
			rce=Reg_Costos_Extra.objects.filter(fecha__range=(fecha_inicial,fecha_final))


			for x in rce:
				if x.caja.sucursal == sucursal:
					cont_reimpresion_boleta = cont_reimpresion_boleta+1
					importe_reimpresion_boleta = importe_reimpresion_boleta+x.importe

			oi = Otros_Ingresos.objects.filter(sucursal=sucursal,fecha__range=(fecha_inicial,fecha_final)).aggregate(Sum("importe"))

			cont_otros=cont_otros+Otros_Ingresos.objects.filter(sucursal=sucursal,fecha__range=(fecha_inicial,fecha_final)).count()

			if oi["importe__sum"]!=None:
				importe_otros=decimal.Decimal(importe_otros)+decimal.Decimal(oi["importe__sum"])

			ret=Retiro_Efectivo.objects.filter(sucursal=sucursal,fecha__range=(fecha_inicial,fecha_final),activo = 1).aggregate(Sum("importe"))

			importe_retiros=0.00			
			cont_retiros=0
			if ret["importe__sum"]!=None:
				importe_retiros=ret["importe__sum"]
				cont_retiros=Retiro_Efectivo.objects.filter(sucursal=sucursal,fecha__range=(fecha_inicial,fecha_final),activo = 1).count()




			#obtenemos el importe de boletas activas
			bea=Boleta_Empeno.objects.filter(estatus=est_activa,sucursal=sucursal).aggregate(Sum("avaluo"))
			be=Boleta_Empeno.objects.filter(estatus=est_activa,sucursal=sucursal).aggregate(Sum("mutuo"))
			cont_activas=Boleta_Empeno.objects.filter(estatus=est_activa,sucursal=sucursal).count()

			mutuo_activo=0.00
			if be["mutuo__sum"]!=None:
				mutuo_activo=be["mutuo__sum"]

			avaluo_activo=0.00
			if bea["avaluo__sum"]!=None:
				avaluo_activo=bea["avaluo__sum"]

			#obtenemos el importe de boletas en almoneda
			bea = Boleta_Empeno.objects.filter(estatus = est_almoneda,sucursal = sucursal).aggregate(Sum("avaluo"))
			be = Boleta_Empeno.objects.filter(estatus = est_almoneda,sucursal = sucursal).aggregate(Sum("mutuo"))
			cont_almoneda = Boleta_Empeno.objects.filter(estatus = est_almoneda,sucursal = sucursal).count()

			mutuo_almoneda=0.00
			if be["mutuo__sum"]!=None:
				mutuo_almoneda=be["mutuo__sum"]

			avaluo_almoneda=0.00
			if bea["avaluo__sum"]!=None:
				avaluo_almoneda=bea["avaluo__sum"]


			bea=Boleta_Empeno.objects.filter(estatus=est_remate,sucursal=sucursal).aggregate(Sum("avaluo"))
			be=Boleta_Empeno.objects.filter(estatus=est_remate,sucursal=sucursal).aggregate(Sum("mutuo"))
			cont_remate=Boleta_Empeno.objects.filter(estatus=est_remate,sucursal=sucursal).count()

			mutuo_remate=0.00
			if be["mutuo__sum"]!=None:
				mutuo_remate=be["mutuo__sum"]

			avaluo_remate=0.00
			if bea["avaluo__sum"]!=None:
				avaluo_remate=bea["avaluo__sum"]

			abonos=Abono.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=sucursal)

			est_com_pg=Tipo_Pago.objects.get(id=2)
			est_refrendo=Tipo_Pago.objects.get(id=1)

			for a in abonos:
				try:
					ra=Rel_Abono_Capital.objects.get(abono=a)
					if decimal.Decimal(ra.capital_restante)<=decimal.Decimal(0):
						#buscams los desempeñs
						cont_desempenos=cont_desempenos+1
						importe_desempenos=decimal.Decimal(importe_desempenos)+decimal.Decimal(ra.importe)
					else:
						#buscamos los abonos  a capital
						cont_capital=cont_capital+1
						importe_capital=decimal.Decimal(importe_capital)+decimal.Decimal(ra.importe)
				except:
					cont_desempenos=cont_desempenos

				#pagos de refrendo 4 semanas
				try:	

					ra=Rel_Abono_Pago.objects.filter(abono=a)

					#busamos si el abono afecto a refrendos.
					rel_ab_pagos_ref=Rel_Abono_Pago.objects.filter(abono=a,pago__tipo_pago=est_refrendo)
					
					#si el abono afecto a pagos tipo refrendo, contamos en 1 el abono a refrendos
					if rel_ab_pagos_ref.exists():
						cont_refrendos=cont_refrendos+1

					#buscamos si el abono afecto a comision PG
					rel_ab_pagos_pg=Rel_Abono_Pago.objects.filter(abono=a,pago__tipo_pago=est_com_pg)

					if rel_ab_pagos_pg.exists():
						cont_com_pg=cont_com_pg+1


					for x in ra:
						if x.pago.tipo_pago!=est_com_pg:
							importe_refrendo=decimal.Decimal(importe_refrendo)+x.pago.importe
							#cont_refrendos=cont_refrendos+1		

						if x.pago.tipo_pago==est_com_pg:
							importe_com_pg=decimal.Decimal(importe_com_pg)+x.pago.importe
							#cont_com_pg=cont_com_pg+1	

				except Exception as e:
					print(e)
					importe_refrendo=importe_refrendo

				#pago refrendo mensual
				try:
					rp=Rel_Abono_Periodo.objects.filter(abono=a)
					#las boletas de plazo mensual se pagan en periodos			
					rap=Rel_Abono_Periodo.objects.filter(abono=a)
					if rap.exists():
						cont_refrendos=cont_refrendos+1
					for x in rp:												
						importe_refrendo=decimal.Decimal(x.periodo.importe)+decimal.Decimal(importe_refrendo)						
						#cont_refrendos=cont_refrendos+1
				except:
					importe_refrendo=importe_refrendo

		else:#en caso de no seleccionar una sucursal, se calcula para todas las sucursales.			
			txt_sucursal="TODAS"			
			try:
				cajas_dia_inicial=Cajas.objects.filter(fecha__range=(fec_inicial_caja,fec_final_caja)).aggregate(Sum("importe"))
				saldo_inicial=0.00
				if cajas_dia_inicial["importe__sum"]!=None:
					saldo_inicial=cajas_dia_inicial["importe__sum"]

			except Exception as e:
				print(e)
				error="Error al consultar el fondo incial"
				est_error="1"
				saldo_inicial=0.00	

			fecha_inicial=datetime.combine(fecha_inicial,time.min)
			fecha_final=datetime.combine(fecha_final,time.max)

			sucursales_aux = Sucursal.objects.all()

			for s in sucursales_aux:				
				refrendo_aux = decimal.Decimal(refrendo_aux) + decimal.Decimal(s.fn_get_total_refrendos(dia_primero_mes,dia_ultimo_mes))
				cpg_aux = decimal.Decimal(cpg_aux) + decimal.Decimal(s.fn_get_total_comision_pg(dia_primero_mes,dia_ultimo_mes))
				ce_aux = decimal.Decimal(ce_aux) + decimal.Decimal(s.fn_get_total_costos_extras(dia_primero_mes,dia_ultimo_mes))			
				ganancia_ventas_aux = decimal.Decimal(ganancia_ventas_aux) + decimal.Decimal(s.fn_get_ganancia_ventas(dia_primero_mes,dia_ultimo_mes))
				im_retiros_aux = decimal.Decimal(im_retiros_aux) + decimal.Decimal(s.fn_get_retiros(dia_primero_mes,dia_ultimo_mes))
			
			cont_ab_apartado=Abono_Apartado.objects.filter(fecha__range=(fecha_inicial,fecha_final)).count()

			iaa=Abono_Apartado.objects.filter(fecha__range=(fecha_inicial,fecha_final)).aggregate(Sum("importe"))

			if iaa["importe__sum"] != None:
				importe_ab_apartado = iaa["importe__sum"]

			#buscamos ingresos por ventas
			cont_ventas=Venta_Granel.objects.filter(fecha_importe_venta__range=(fecha_inicial,fecha_final)).count()
			imp_venta=Venta_Granel.objects.filter(fecha_importe_venta__range=(fecha_inicial,fecha_final)).aggregate(Sum("importe_venta"))

			importe_ventas=0	
			if imp_venta["importe_venta__sum"]==None:
				importe_ventas=0.00
			else:
				importe_ventas=imp_venta["importe_venta__sum"]


			#buscamos ingresos por ventas piso
			cont_ventas=cont_ventas+Venta_Piso.objects.filter(fecha__range=(fecha_inicial,fecha_final)).count()

			imp_venta=Venta_Piso.objects.filter(fecha__range=(fecha_inicial,fecha_final)).aggregate(Sum("importe_venta"))	
			if imp_venta["importe_venta__sum"]==None:
				print("")
			else:
				importe_ventas=decimal.Decimal(importe_ventas)+decimal.Decimal(imp_venta["importe_venta__sum"])


			#calculamos el resumen de la venta piso
			cont_venta_piso=Venta_Piso.objects.filter(fecha__range=(fecha_inicial,fecha_final)).count()
			imp_venta=Venta_Piso.objects.filter(fecha__range=(fecha_inicial,fecha_final)).aggregate(Sum("importe_venta"))	
			imp_av_vp=Venta_Piso.objects.filter(fecha__range=(fecha_inicial,fecha_final)).aggregate(Sum("importe_avaluo"))	
			imp_mut_vp=Venta_Piso.objects.filter(fecha__range=(fecha_inicial,fecha_final)).aggregate(Sum("importe_mutuo"))	

			if imp_venta["importe_venta__sum"]==None:
				print("")
			else:
				importe_venta_piso=decimal.Decimal(imp_venta["importe_venta__sum"])

			if imp_av_vp["importe_avaluo__sum"]==None:
				print("")
			else:
				importe_avaluo_piso=decimal.Decimal(imp_av_vp["importe_avaluo__sum"])

			if imp_mut_vp["importe_mutuo__sum"]==None:
				print("")
			else:
				importe_mutuo_piso=decimal.Decimal(imp_mut_vp["importe_mutuo__sum"])


			#calculamos el resumen de la venta piso
			cont_venta_granel=Venta_Granel.objects.filter(fecha__range=(fecha_inicial,fecha_final)).count()
			imp_venta=Venta_Granel.objects.filter(fecha__range=(fecha_inicial,fecha_final)).aggregate(Sum("importe_venta"))	
			imp_av_vg=Venta_Granel.objects.filter(fecha__range=(fecha_inicial,fecha_final)).aggregate(Sum("importe_avaluo"))	
			imp_mut_vg=Venta_Granel.objects.filter(fecha__range=(fecha_inicial,fecha_final)).aggregate(Sum("importe_mutuo"))	


			if imp_venta["importe_venta__sum"]==None:
				print("")
			else:
				importe_venta_granel=decimal.Decimal(imp_venta["importe_venta__sum"])

			if imp_av_vg["importe_avaluo__sum"]==None:
				print("")
			else:
				importe_avaluo_granel=decimal.Decimal(imp_av_vg["importe_avaluo__sum"])

			if imp_mut_vg["importe_mutuo__sum"]==None:
				print("")
			else:
				importe_mutuo_granel=decimal.Decimal(imp_mut_vg["importe_mutuo__sum"])




			#calculamos los empeños
			importe_empenos=Boleta_Empeno.objects.filter(fecha__range=(fecha_inicial,fecha_final)).aggregate(Sum("mutuo_original"))
			cont_empenos=Boleta_Empeno.objects.filter(fecha__range=(fecha_inicial,fecha_final)).exclude(estatus__id = 2).count()

			if importe_empenos["mutuo_original__sum"]==None:
				importe_empenos=0.00
			else:
				importe_empenos=importe_empenos["mutuo_original__sum"]

			#obtenemos los costos extras
			rce=Reg_Costos_Extra.objects.filter(fecha__range=(fecha_inicial,fecha_final))

			for x in rce:
				cont_reimpresion_boleta = cont_reimpresion_boleta+1
				importe_reimpresion_boleta = importe_reimpresion_boleta+x.importe

			oi=Otros_Ingresos.objects.filter(fecha__range=(fecha_inicial,fecha_final)).aggregate(Sum("importe"))

			cont_otros=cont_otros+Otros_Ingresos.objects.filter(fecha__range=(fecha_inicial,fecha_final)).count()

			if oi["importe__sum"]!=None:
				importe_otros=decimal.Decimal(importe_otros)+decimal.Decimal(oi["importe__sum"])

			ret=Retiro_Efectivo.objects.filter(fecha__range=(fecha_inicial,fecha_final),activo = 1).aggregate(Sum("importe"))

			importe_retiros=0.00			
			cont_retiros=0
			if ret["importe__sum"]!=None:
				importe_retiros=ret["importe__sum"]
				cont_retiros=Retiro_Efectivo.objects.filter(fecha__range=(fecha_inicial,fecha_final),activo = 1).count()



			#obtenemos el importe de boletas activas
			bea=Boleta_Empeno.objects.filter(estatus=est_activa).aggregate(Sum("avaluo"))
			be=Boleta_Empeno.objects.filter(estatus=est_activa).aggregate(Sum("mutuo"))
			cont_activas=Boleta_Empeno.objects.filter(estatus=est_activa).count()

			mutuo_activo=0.00
			if be["mutuo__sum"]!=None:
				mutuo_activo=be["mutuo__sum"]

			avaluo_activo=0.00
			if bea["avaluo__sum"]!=None:
				avaluo_activo=bea["avaluo__sum"]

			#obtenemos el importe de boletas en almoneda
			bea=Boleta_Empeno.objects.filter(estatus=est_almoneda).aggregate(Sum("avaluo"))
			be=Boleta_Empeno.objects.filter(estatus=est_almoneda).aggregate(Sum("mutuo"))
			cont_almoneda=Boleta_Empeno.objects.filter(estatus=est_almoneda).count()

			mutuo_almoneda=0.00
			if be["mutuo__sum"]!=None:
				mutuo_almoneda=be["mutuo__sum"]

			avaluo_almoneda=0.00
			if bea["avaluo__sum"]!=None:
				avaluo_almoneda=bea["avaluo__sum"]

			bea=Boleta_Empeno.objects.filter(estatus=est_remate).aggregate(Sum("avaluo"))
			be=Boleta_Empeno.objects.filter(estatus=est_remate).aggregate(Sum("mutuo"))
			cont_remate=Boleta_Empeno.objects.filter(estatus=est_remate).count()

			mutuo_remate=0.00
			if be["mutuo__sum"]!=None:
				mutuo_remate=be["mutuo__sum"]

			avaluo_remate=0.00
			if bea["avaluo__sum"]!=None:
				avaluo_remate=bea["avaluo__sum"]


			abonos=Abono.objects.filter(fecha__range=(fecha_inicial,fecha_final))

			est_com_pg=Tipo_Pago.objects.get(id=2)
			est_refrendo=Tipo_Pago.objects.get(id=1)

			for a in abonos:
				try:
					ra=Rel_Abono_Capital.objects.get(abono=a)
					if decimal.Decimal(ra.capital_restante)<=decimal.Decimal(0):
						#buscams los desempeñs
						cont_desempenos=cont_desempenos+1
						importe_desempenos=decimal.Decimal(importe_desempenos)+decimal.Decimal(ra.importe)
					else:
						#buscamos los abonos  a capital
						cont_capital=cont_capital+1
						importe_capital=decimal.Decimal(importe_capital)+decimal.Decimal(ra.importe)
				except:
					cont_desempenos=cont_desempenos

				#pagos de refrendo 4 semanas
				try:	

					ra=Rel_Abono_Pago.objects.filter(abono=a)


					#busamos si el abono afecto a refrendos.
					rel_ab_pagos_ref=Rel_Abono_Pago.objects.filter(abono=a,pago__tipo_pago=est_refrendo)
					
					#si el abono afecto a pagos tipo refrendo, contamos en 1 el abono a refrendos
					if rel_ab_pagos_ref.exists():
						cont_refrendos=cont_refrendos+1

					#buscamos si el abono afecto a comision PG
					rel_ab_pagos_pg=Rel_Abono_Pago.objects.filter(abono=a,pago__tipo_pago=est_com_pg)

					if rel_ab_pagos_pg.exists():
						cont_com_pg=cont_com_pg+1


					for x in ra:
						if x.pago.tipo_pago!=est_com_pg:
							importe_refrendo=decimal.Decimal(importe_refrendo)+x.pago.importe
							#cont_refrendos=cont_refrendos+1		

						if x.pago.tipo_pago==est_com_pg:
							importe_com_pg=decimal.Decimal(importe_com_pg)+x.pago.importe
							#cont_com_pg=cont_com_pg+1		

				except Exception as e:
					print(e)
					importe_refrendo=importe_refrendo

				#pago refrendo mensual
				try:
					rp=Rel_Abono_Periodo.objects.filter(abono=a)

					#las boletas de plazo mensual se pagan en periodos			
					rap=Rel_Abono_Periodo.objects.filter(abono=a)
					if rap.exists():
						cont_refrendos=cont_refrendos+1

					for x in rp:												
						importe_refrendo=decimal.Decimal(x.periodo.importe)+decimal.Decimal(importe_refrendo)						
						#cont_refrendos=cont_refrendos+1
				except:
					importe_refrendo=importe_refrendo

	else:	
		post="0"


	form=Flujo_Caja_Form()


	

	
	

	cont_t_entradas = 1 + cont_otros + cont_com_pg + cont_refrendos + cont_capital + cont_desempenos + cont_ventas + cont_ab_apartado + cont_reimpresion_boleta
	importe_t_entradas  = math.ceil(float(saldo_inicial) + float(importe_desempenos) + float(importe_capital) + float(importe_refrendo) + float(importe_com_pg) + float(importe_otros) + float(importe_reimpresion_boleta) + float(importe_ventas) + float(importe_ab_apartado) )



	cont_t_salidas = cont_retiros + cont_empenos
	importe_t_salidas = math.ceil( float(importe_empenos) + float(importe_retiros))
	

	importe_refrendo=round(importe_refrendo)

	importe_total = decimal.Decimal(importe_ab_apartado) + decimal.Decimal(saldo_inicial) - decimal.Decimal(importe_empenos) + decimal.Decimal(importe_desempenos)+decimal.Decimal(importe_capital)+decimal.Decimal(importe_refrendo)+decimal.Decimal(importe_com_pg)+decimal.Decimal(importe_otros)-decimal.Decimal(importe_retiros)+decimal.Decimal(importe_ventas) + decimal.Decimal(importe_reimpresion_boleta)

	importe_total=math.ceil(importe_total)

	cont_total=1+cont_otros+cont_com_pg+cont_refrendos+cont_capital+cont_desempenos+cont_empenos+cont_ventas+cont_ab_apartado+cont_retiros + cont_reimpresion_boleta

	cont_total_2=cont_almoneda+cont_activas+cont_remate

			
	total_utilidad = decimal.Decimal(refrendo_aux) + decimal.Decimal(cpg_aux) + decimal.Decimal(ce_aux) + decimal.Decimal(ganancia_ventas_aux) - decimal.Decimal(im_retiros_aux)


	ganancias_t = float(ganancia_ventas_aux) + float(ce_aux) + float(cpg_aux) + float(refrendo_aux)

	ganancias_t = "{:0,.2f}".format(ganancias_t)
	
	refrendo_aux = "{:0,.2f}".format(refrendo_aux)
	cpg_aux = "{:0,.2f}".format(cpg_aux)
	ce_aux = "{:0,.2f}".format(ce_aux)
	ganancia_ventas_aux = "{:0,.2f}".format(ganancia_ventas_aux)

	total_utilidad = "{:0,.2f}".format(total_utilidad)


	total_mutuo=mutuo_almoneda+mutuo_activo+mutuo_remate
	total_almoneda=avaluo_almoneda+avaluo_activo+avaluo_remate
	#damos formato a las variables
	importe_empenos="{:0,.2f}".format(importe_empenos)
	saldo_inicial="{:0,.2f}".format(saldo_inicial)
	importe_desempenos="{:0,.2f}".format(importe_desempenos)
	importe_capital="{:0,.2f}".format(importe_capital)
	
	importe_refrendo="{:0,.2f}".format(importe_refrendo)
	importe_com_pg="{:0,.2f}".format(importe_com_pg)
	importe_otros="{:0,.2f}".format(importe_otros)
	mutuo_activo="{:0,.2f}".format(mutuo_activo)
	avaluo_activo="{:0,.2f}".format(avaluo_activo)
	mutuo_almoneda="{:0,.2f}".format(mutuo_almoneda)
	avaluo_almoneda="{:0,.2f}".format(avaluo_almoneda)
	importe_ventas="{:0,.2f}".format(importe_ventas)

	mutuo_remate = "{:0,.2f}".format(mutuo_remate)
	avaluo_remate = "{:0,.2f}".format(avaluo_remate)
	im_retiros_aux = "{:0,.2f}".format(im_retiros_aux)
	importe_total="{:0,.2f}".format(importe_total)
	total_mutuo="{:0,.2f}".format(total_mutuo)
	total_almoneda="{:0,.2f}".format(total_almoneda)
	importe_retiros="{:0,.2f}".format(importe_retiros)

	utilidad_vta_piso=decimal.Decimal(importe_venta_piso)-decimal.Decimal(importe_mutuo_piso)
	utilidad_vta_granel=decimal.Decimal(importe_venta_granel)-decimal.Decimal(importe_mutuo_granel)

	tot_venta="{:0,.2f}".format(decimal.Decimal(importe_venta_piso)+decimal.Decimal(importe_venta_granel))
	tot_avaluo="{:0,.2f}".format(decimal.Decimal(importe_avaluo_piso)+decimal.Decimal(importe_avaluo_granel))
	tot_mutuo="{:0,.2f}".format(decimal.Decimal(importe_mutuo_piso)+decimal.Decimal(importe_mutuo_granel))
	tot_utilidad_vta="{:0,.2f}".format(decimal.Decimal(utilidad_vta_piso)+decimal.Decimal(utilidad_vta_granel))


	cont_total_vta=cont_venta_granel+cont_venta_piso


	#cont_t_entradas = "{:0,.2f}".format(cont_t_entradas)
	importe_t_entradas  = "{:0,.2f}".format(importe_t_entradas)



	#cont_t_salidas = "{:0,.2f}".format(cont_t_salidas)
	importe_t_salidas = "{:0,.2f}".format(importe_t_salidas)
	

	importe_ab_apartado = "{:0,.2f}".format(importe_ab_apartado)
	
	importe_venta_piso="{:0,.2f}".format(importe_venta_piso)
	importe_avaluo_piso="{:0,.2f}".format(importe_avaluo_piso)
	importe_mutuo_piso="{:0,.2f}".format(importe_mutuo_piso)
	utilidad_vta_piso="{:0,.2f}".format(utilidad_vta_piso)
	
	importe_venta_granel="{:0,.2f}".format(importe_venta_granel)
	importe_avaluo_granel="{:0,.2f}".format(importe_avaluo_granel)
	importe_mutuo_granel="{:0,.2f}".format(importe_mutuo_granel)
	utilidad_vta_granel="{:0,.2f}".format(utilidad_vta_granel)

	sucursal_default=user_2.sucursal.id
	#cuando eres gerente regiona, puedes entrar a todas las sucursales
	if user_2.perfil.id==3:		
		sucursales=Sucursal.objects.all()		
	else:#cuando no eres gerente regional, solo puedes acceder a tu sucursal.

		sucursales=Sucursal.objects.filter(id=user_2.sucursal.id)

		

	perfil=str(user_2.perfil.id)

	return render(request,'empenos/rep_flujo_caja.html',locals())

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
def retiro_efectivo(request):
	id_retiro = "0"

	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))


	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)


	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  
	fondo_inicial=0.00
	otros_ingresos=0.00
	retiros=0.00
	empenos=0.00
	total_movs=1#se empieza a contar 1 porque hubo  al menos una apertura de cajero
	total_efectivo=0.00
	
	try:

		#validamos si el usuario tiene caja abierta en el dia actual.,si no tiene fecha de cierre es prque aun no ha sido cerrada.
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=user_2.user)
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja
		fondo_inicial=caja.importe

	except Exception as e:
		print(e)
		#si mandamos este estatus es que hay que bloquear el acceos ya que no tiene caja abierta
		caja_abierta = "0"
		caja = Cajas
		form = Retiro_Efectivo_Form()
		return render(request,'empenos/retiro_efectivo.html',locals())

	#buscamos las reimpresiones de boleta
	cont_rebol = Reg_Costos_Extra.objects.filter(caja = caja).count()
	sum_importe_rebol = Reg_Costos_Extra.objects.filter(caja = caja).aggregate(Sum('importe'))

	importe_rebol = 0.00
	if sum_importe_rebol["importe__sum"] == None:
		importe_rebol = 0.00
	else:
		importe_rebol = int(sum_importe_rebol["importe__sum"])



	#como solo se puede abrir una caja por sucursal al dia (el usuario virtual la abre)	
	try:
		#oi=Otros_Ingresos.objects.filter(sucursal=suc,usuario=request.user,fecha__range=(min_pub_date_time,max_pub_date_time),caja=c).aggregate(Sum('importe'))
		oi=Otros_Ingresos.objects.filter(ocaja = caja).aggregate(Sum('importe'))
		cont_otros_ingresos = Otros_Ingresos.objects.filter(ocaja = caja).count()
		total_movs = total_movs + cont_otros_ingresos

		if oi["importe__sum"]!= None:
			otros_ingresos=oi["importe__sum"]

	except Exception as e:
		print(e)
		print("no tiene otros ingresos.")



	#buscamos los retiros
	try:
		ret=Retiro_Efectivo.objects.filter(ocaja = caja,activo = 1).aggregate(Sum('importe'))
		cont_retiros=Retiro_Efectivo.objects.filter(ocaja = caja,activo = 1).count()
		total_movs=total_movs+cont_retiros #sumamos el total de retiros al total de movimientos
		if ret["importe__sum"]!=None:
			retiros=ret["importe__sum"]
	except Exception as e:
		print(e)
		print("No tiene retiros.")


	try:
		emp=Boleta_Empeno.objects.filter(caja=caja).aggregate(Sum("mutuo_original"))

		cont_empenos=Boleta_Empeno.objects.filter(caja=caja).exclude(estatus__id = 2).count()
		total_movs=total_movs+cont_empenos
		if emp["mutuo_original__sum"]!=None:
			empenos=emp["mutuo_original__sum"]
	except Exception as e:
		print(e)
		print("No tiene empenños")


	#buscamos ingresos por ventas
	cont_ventas=Venta_Granel.objects.filter(fecha_importe_venta__range=(min_pub_date_time,max_pub_date_time),caja=caja).count()
	imp_venta=Venta_Granel.objects.filter(fecha_importe_venta__range=(min_pub_date_time,max_pub_date_time),caja=caja).aggregate(Sum("importe_venta"))

	importe_ventas=0	
	if imp_venta["importe_venta__sum"]==None:
		importe_ventas=0.00
	else:
		importe_ventas=imp_venta["importe_venta__sum"]

	#buscamos ingresos por ventas piso
	cont_ventas=cont_ventas+Venta_Piso.objects.filter(caja=caja).count()

	imp_venta=Venta_Piso.objects.filter(caja=caja).aggregate(Sum("importe_venta"))	
	if imp_venta["importe_venta__sum"]==None:
		print("")
	else:
		importe_ventas=decimal.Decimal(importe_ventas)+decimal.Decimal(imp_venta["importe_venta__sum"])


	cont_ref_pg=0
	refrendos_pg=0.00

	cont_com_pg=0
	comisiones_pg=0.00

	cont_pc=0
	pago_capital=0.00

	cont_refrendos=0
	importe_refrendo=0.00

	importe_desemp=0.00
	cont_desemp=0

	cont_ab_apartado = 0
	importe_apartado = 0

	cont_ab_apartado=Abono_Apartado.objects.filter(caja = caja).count()
	ia=Abono_Apartado.objects.filter(caja = caja).aggregate(Sum('importe'))

	if ia["importe__sum"] != None:
		importe_apartado = ia["importe__sum"]

	try:
		
		#buscamos el pago a comisiones PG
		abonos=Abono.objects.filter(caja=caja)#todos los abonos echos por la caja.

		est_refrendo=Tipo_Pago.objects.get(id=1)

		est_com_pg=Tipo_Pago.objects.get(id=2)

		est_ref_pg=Tipo_Pago.objects.get(id=3)
		
		for ab in abonos:
			rel_ab_pagos=Rel_Abono_Pago.objects.filter(abono=ab)#buscamos a que pago le pego cada refrendo

			#busamos si el abono afecto a refrendos.
			rel_ab_pagos_ref=Rel_Abono_Pago.objects.filter(abono=ab,pago__tipo_pago=est_refrendo)
			
			#si el abono afecto a pagos tipo refrendo, contamos en 1 el abono a refrendos
			if rel_ab_pagos_ref.exists():
				cont_refrendos=cont_refrendos+1

			#buscamos si el abono afecto a comision PG
			rel_ab_pagos_pg=Rel_Abono_Pago.objects.filter(abono=ab,pago__tipo_pago=est_com_pg)

			if rel_ab_pagos_pg.exists():
				cont_com_pg=cont_com_pg+1

			for p in rel_ab_pagos:
				
				if p.pago.tipo_pago==est_refrendo:#si afecto a refrendo acumulamos el importe.
					
					importe_refrendo=decimal.Decimal(importe_refrendo)+decimal.Decimal(p.pago.importe)

				if p.pago.tipo_pago==est_com_pg:#si afecto a comision pg acumulamos el importe.
					
					comisiones_pg=decimal.Decimal(comisiones_pg)+decimal.Decimal(p.pago.importe)

				if p.pago.tipo_pago==est_ref_pg:#si afecto a refrebdis pg acumulamos el importe.
					
					importe_refrendo=decimal.Decimal(importe_refrendo)+decimal.Decimal(p.pago.importe)

			#las boletas de plazo mensual se pagan en periodos			
			rap=Rel_Abono_Periodo.objects.filter(abono=ab)
			if rap.exists():
				cont_refrendos=cont_refrendos+1
			for x in rap:
				#cont_refrendos=cont_refrendos+1
				importe_refrendo=decimal.Decimal(importe_refrendo)+decimal.Decimal(x.periodo.importe)

			importe_refrendo=round(importe_refrendo)

			
			rel_ab_cap = Rel_Abono_Capital.objects.filter(abono=ab).exclude(capital_restante=0).aggregate(Sum("importe"))#buscamos si el abono afecto a capital
			cont_pc=cont_pc+Rel_Abono_Capital.objects.filter(abono=ab).exclude(capital_restante=0).count()

			
			if rel_ab_cap["importe__sum"]==None:
				pago_capital = pago_capital+0
			else:
				pago_capital = pago_capital+int(rel_ab_cap["importe__sum"])

			rel_desem=Rel_Abono_Capital.objects.filter(abono=ab)#.exclude(capital_restante__gte=0).aggregate(Sum("importe"))#buscamos si el abono afecto a capital
			#cont_desemp=cont_desemp+Rel_Abono_Capital.objects.filter(abono=ab).exclude(capital_restante__gte=0).count()

			for x in rel_desem:
				if decimal.Decimal(x.capital_restante)==decimal.Decimal(0):
					importe_desemp=decimal.Decimal(importe_desemp)+decimal.Decimal(x.importe)
					cont_desemp=int(cont_desemp)+1

			
		#total_movs=total_movs+int(cont_com_pg)+int(cont_ref_pg)+int(cont_pc)+int(cont_refrendos)+int(cont_rebol)+int(cont_desemp)+int(cont_ventas)
	
	except Exception as e:

		print(e)
		print("No se han registrado abonos.")



	total_movs=total_movs+int(cont_com_pg)+int(cont_ref_pg)+int(cont_pc)+int(cont_refrendos)+int(cont_rebol)+int(cont_desemp)+int(cont_ventas)+int(cont_ab_apartado)
	

	#total=fondo_inicial+otros_ingresos-retiros_caja
	total_efectivo=decimal.Decimal(fondo_inicial)+decimal.Decimal(importe_apartado)+decimal.Decimal(otros_ingresos)-decimal.Decimal(retiros)-decimal.Decimal(empenos)+decimal.Decimal(pago_capital)+decimal.Decimal(comisiones_pg)+decimal.Decimal(refrendos_pg)+decimal.Decimal(importe_refrendo)+decimal.Decimal(importe_rebol)+decimal.Decimal(importe_desemp)+decimal.Decimal(importe_ventas)

	#es la clave para retiros de caja.
	tm=Tipo_Movimiento.objects.get(id=3)

	error_no_fondos='0'
	read_only="0"

	fondo_inicial="{:0,.2f}".format(fondo_inicial)
	otros_ingresos="{:0,.2f}".format(otros_ingresos)
	importe_refrendo="{:0,.2f}".format(importe_refrendo)
	
	comisiones_pg="{:0,.2f}".format(comisiones_pg)

	pago_capital="{:0,.2f}".format(pago_capital)
	importe_desemp="{:0,.2f}".format(importe_desemp)
	importe_rebol="{:0,.2f}".format(importe_rebol)
	importe_ventas="{:0,.2f}".format(importe_ventas)
	importe_apartado="{:0,.2f}".format(importe_apartado)
	retiros="{:0,.2f}".format(retiros)

	empenos="{:0,.2f}".format(empenos)

	#total_efectivo="{:0,.2f}".format(total_efectivo)

	conceptos = Concepto_Retiro.objects.filter(sucursal = caja.sucursal, activo = 1)
	
	id_concepto = ""

	#0 para indicar que todo esta oc
	#1 para indicar que no tiene caja abierta
	error_caja_destino = "0"
	if request.method=="POST":
		read_only="1"

		form=Retiro_Efectivo_Form(request.POST)				

		folio=fn_folios(tm,suc)
		str_folio=fn_str_clave(folio)

		token=None
		#el usuario debe tener token
		try:
			q_token = Token.objects.get(tipo_movimiento=tm,sucursal=suc,caja=c,usuario=request.user)
			token = q_token.token
			concepto =Concepto_Retiro.objects.get(id = q_token.aux_1) 
		except:
			print("no hay token")

		#validamos si es traspaso
		#si tiene registrada una sucursal destino es que es traspaso
		if concepto.sucursal_destino != None:
			#obtenemos la caja de la sucursal destino
			caja_destino = concepto.sucursal_destino.fn_get_caja_abierta()
			if caja_destino == None:
				error_caja_destino = "1"
				return render(request,'empenos/retiro_efectivo.html',locals())

		saldo_concepto = concepto.fn_saldo_concepto()		

		error_saldo_concepto = "0"
		if int(saldo_concepto) >= int(request.POST["importe"]):	
			pass#
			error_saldo_concepto = "0"
		else:			
			error_saldo_concepto = "1"
			
			return render(request,'empenos/retiro_efectivo.html',locals())
		with transaction.atomic():
			if form.is_valid():
				#with transaction.atomic():
				f=form.save(commit=False)
				error_token='0'
				id_concepto = f.concepto.id
				try:
					#validamos el token de seguridad
					
					
					if f.token!=token:
						error_token='1'
						return render(request,'empenos/retiro_efectivo.html',locals())
				except Exception as e:
					print(e)
					error_token='1'
					#transaction.set_rollback(True)
					return render(request,'empenos/retiro_efectivo.html',locals())
					

				#validamos que la caja tenga fondos suficiente para realizar el retiro.
				if total_efectivo<f.importe:
					error_no_fondos='1'
					#transaction.set_rollback(True)
					return render(request,'empenos/retiro_efectivo.html',locals())

				f.folio=str_folio
				f.sucursal=suc
				f.caja=c
				f.usuario=request.user
				f.concepto = concepto
				f.ocaja = caja
				f.save()

				id_retiro = f.id
				
				retiro = Retiro_Efectivo.objects.get(id =int(id_retiro))

				#validamos si es traspaso
				#Si es traspaso generamos el ingreso en la sucursal destino
				if concepto.sucursal_destino != None:
					#es la clave para otros ingresos.
					tm=Tipo_Movimiento.objects.get(id=2)
					folio=fn_folios(tm,concepto.sucursal_destino)
					str_folio=fn_str_clave(folio)

					#damos de alta el ingreso en la sucursal destino
					oi = Otros_Ingresos()			
					oi.folio = str_folio
					oi.tipo_movimiento = tm
					oi.sucursal = concepto.sucursal_destino
					oi.usuario = request.user
					oi.importe = retiro.importe
					oi.comentario = retiro.comentario
					oi.caja = "A"
					oi.ocaja = caja_destino
					oi.save()

					tes = Traspaso_Entre_Sucursales()
					tes.retiro = retiro
					tes.ingreso = oi
					tes.save()
	else:

		try:
		#si ya existe un tocken para esta transaccion la eliminamos
			Token.objects.get(tipo_movimiento=tm,sucursal=suc,caja=c,usuario=request.user).delete()
		except:
			print("No tenia token asignado.")

		error_no_fondos="0"

		#generams el token	
		token=fn_genera_token()
		Token.objects.create(tipo_movimiento=tm,sucursal=suc,caja=c,usuario=request.user,token=token)

		asunto	="Retiro de Efectivo"
		usuario =request.user.first_name+' '+request.user.last_name
		sucursal=suc
		caja=c	
		error_token='0'
		form=Retiro_Efectivo_Form()
	return render(request,'empenos/retiro_efectivo.html',locals())

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
# a esta pantalla solo pueden entrar el gerente de sucursal y el gerente regional.
def corte_caja(request):


	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	c=""

	if caja != None:
		c = caja.caja
		#return render(request,'login.html',locals())

	IP_LOCAL = settings.IP_LOCAL

	perfil_valido = '1'

	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	id_perfil = user_2.perfil.id

	#sucursales = Sucursales_Regional.objects.filter(user=user_2.user,sucursal=user_2.sucursal)


	is_post="0"
	error_guardar=""
	imprime_comprobante = "0"
	if request.method=='POST':
		is_post="1"
		try:
			#obtenemos la caja que se desea cerrar.
			caja=Cajas.objects.get(token_cierre_caja=request.POST.get("token"))
			caja.centavos_10=request.POST.get("centavos_10")
			caja.centavos_50=request.POST.get("centavos_50")
			caja.pesos_1=request.POST.get("pesos_1")
			caja.pesos_2=request.POST.get("pesos_2")
			caja.pesos_5=request.POST.get("pesos_5")
			caja.pesos_10=request.POST.get("pesos_10")
			caja.pesos_20=request.POST.get("pesos_20")
			caja.pesos_50=request.POST.get("pesos_50")
			caja.pesos_100=request.POST.get("pesos_100")
			caja.pesos_200=request.POST.get("pesos_200")
			caja.pesos_500=request.POST.get("pesos_500")
			caja.pesos_1000=request.POST.get("pesos_1000")
			caja.diferencia=request.POST.get("diferencia")
			caja.real_efectivo=request.POST.get("real_efectivo")
			caja.comentario=request.POST.get("comentario")
			caja.estatus_guardado=1			
			caja.fecha_cierre=datetime.now()
			caja.user_cierra_caja=request.user
			caja.save()	

			#actualizamos el saldo de la sucursal
			caja.sucursal.saldo=caja.teorico_efectivo
			caja.sucursal.save()	

			fn_envia_mail_diferencia_cierre_caja(caja)			

			if caja.fecha.day<10:
				day='0'+str(caja.fecha.day)
			else:
				day=str(caja.fecha.day)

			if caja.fecha.month<10:
				month='0'+str(caja.fecha.month)
			else:
				month=str(caja.fecha.month)
			year=str(caja.fecha.year)

			fecha_post=year+'-'+month+'-'+day
			
			today = date.today()

			
			imprime_comprobante = str(caja.id)

		except Exception as e:
			error_guardar="Error al cerrar la caja."
			print(e)
			print("no pudo guardar")
		form=Cierra_Caja_Form()
	else:
		form=Cierra_Caja_Form()
	return render(request,'empenos/corte_caja.html',locals())

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
"""
idpermiso = 20
"""
def reportes_caja(request):

 
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(20):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))



	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	try:
		id_sucursal=int(request.POST.get("sucursal"))
		#validamos si el usuario tiene caja abierta en el dia actual.
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=request.user)
		caja_abierta="1"#si tiene caja abierta enviamos este estatus para  dejar entrar a la pantalla.
		suc=caja.sucursal
		c=caja.caja

	except Exception as e:
		print(e)
		caja_abierta="0"
		caja=Cajas

	permiso="1"
		
	if request.method=="POST" and permiso=="1":		
		
		id_tipo_movimiento=request.POST.get("id_tipo_mov")
		
		fecha_inicial= datetime.strptime(request.POST.get("fecha_inicial"), "%Y-%m-%d").date()
		fecha_final= datetime.strptime(request.POST.get("fecha_final"), "%Y-%m-%d").date()

		
		fecha_inicial = datetime.combine(fecha_inicial, time.min) 
		fecha_final = datetime.combine(fecha_final, time.max)  

		error="0"


		#apertura de caja
		if id_tipo_movimiento=="1":
			try:
				cajas=Cajas.objects.filter(fecha__range=(fecha_inicial,fecha_final))
			except:
				error="1"
				msj_error="No existen cajas abiertas en la fecha indicada."
				return render(request,'empenos/reportes_caja.html',locals())	

			print(cajas)
			try:
				nom_archivo='Rep_Cajas_'+request.POST.get('fecha_inicial')+'-'+request.POST.get('fecha_final')+'.csv'
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="'+nom_archivo+'"'

				writer = csv.writer(response)

				writer.writerow(['Fecha Apertura','Estatus','User Name Apertura', 'Nombre Usuario Apertura', 'Folio','Sucursal','Importe de Apertura','Caja','Real Efectivo','Teorico Efectivo','Diferencia','1 Peso','2 Pesos','5 Pesos','10 Pesos','20 Pesos','50 Pesos','100 Pesos','200 Pesos','500 Pesos','1000 Pesos','Fecha Cierre','User Name Cierre','Usuario Cierre','Comentario'])

				for c in cajas:				
					estatus="Cerrada"
					nombre_user_cierra=""
					if c.fecha_cierre==None:
						estatus="Abierta"

					if c.user_cierra_caja!=None:
						nombre_user_cierra=c.user_cierra_caja.first_name+''+c.user_cierra_caja.last_name

					txt_usuario_abre = ""
					txt_username = ""
					if c.usuario_real_abre_caja == None:
						txt_usuario_abre = c.usuario.first_name+' '+c.usuario.last_name
						txt_username = c.usuario.username
					else:
						txt_usuario_abre = c.usuario_real_abre_caja.first_name+' '+c.usuario_real_abre_caja.last_name
						txt_username = c.usuario_real_abre_caja.username

					

					writer.writerow([str(c.fecha),estatus, txt_username,txt_usuario_abre , c.folio,c.sucursal.sucursal,c.importe,c.caja,c.real_efectivo,c.teorico_efectivo,c.diferencia,c.pesos_1,c.pesos_2,c.pesos_5,c.pesos_10,c.pesos_20,c.pesos_50,c.pesos_100,c.pesos_200,c.pesos_500,c.pesos_1000,str(c.fecha_cierre),c.user_cierra_caja,nombre_user_cierra,c.comentario])					

				return response
			except:
				error="1"
				msj_error="Error al exportar la información, contacte al administrador del sistema."
				return render(request,'empenos/reportes_caja.html',locals())

		if id_tipo_movimiento=="2":

			try:
				otros_ingresos=Otros_Ingresos.objects.filter(fecha__range=(fecha_inicial,fecha_final))
			except:
				error="1"
				msj_error="No existen ingresos en la fecha indicada."
				return render(request,'empenos/reportes_caja.html',locals())	

			try:
				nom_archivo='Rep_Otros_Ingresos_'+request.POST.get('fecha_inicial')+'-'+request.POST.get('fecha_final')+'.csv'
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="'+nom_archivo+'"'

				writer = csv.writer(response)

				writer.writerow(['Folio','Sucursal','Fecha', 'Nombre Usuario','Usuario', 'Importe','Comentario','Caja'])

				for oi in otros_ingresos:				
					writer.writerow([oi.folio,oi.sucursal.sucursal,str(oi.fecha),oi.usuario.username,oi.usuario.first_name+' '+oi.usuario.last_name, oi.importe,oi.comentario,oi.caja])					

				return response
			except:
				error="1"
				msj_error="Error al exportar la información, contacte al administrador del sistema."
				return render(request,'empenos/reportes_caja.html',locals())
		if id_tipo_movimiento=="3":

			try:
				retiros=Retiro_Efectivo.objects.filter(fecha__range=(fecha_inicial,fecha_final))
			except:
				error="1"
				msj_error="No existen retiros en la fecha indicada."
				return render(request,'empenos/reportes_caja.html',locals())	

			try:
				nom_archivo='Rep_Retiros_'+request.POST.get('fecha_inicial')+'-'+request.POST.get('fecha_final')+'.csv'
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="'+nom_archivo+'"'

				writer = csv.writer(response)

				writer.writerow(['Folio','Sucursal','Fecha','Nombre Usuario','Usuario', 'Importe','Comentario','Caja','Concepto','Activo','Usuario Cancela'])

				for r in retiros:
					if r.concepto == None:
						concepto = ""
					else:
						concepto = r.concepto				

					if r.activo == '1':
						activo = "SI"
					else:
						activo = "NO"

					if r.usuario_cancela == None:
						username = ''
					else:
						username =r.usuario_cancela.username

					writer.writerow([r.folio,r.sucursal.sucursal,r.fecha.strftime('%Y-%m-%d'),r.usuario.username,r.usuario.first_name+' '+r.usuario.last_name, r.importe,r.comentario,r.caja,concepto,activo,username])					

				return response
			except:
				error="1"
				msj_error="Error al exportar la información, contacte al administrador del sistema."
				return render(request,'empenos/reportes_caja.html',locals())
		if id_tipo_movimiento=="4":
			try:
				boletas=Boleta_Empeno.objects.filter(fecha__range=(fecha_inicial,fecha_final)).order_by('folio')
			except:
				error="1"
				msj_error="No existen retiros en la fecha indicada."
				return render(request,'empenos/reportes_caja.html',locals())	

			try:
				nom_archivo='Rep_Boletas_'+request.POST.get('fecha_inicial')+'-'+request.POST.get('fecha_final')+'.csv'
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="'+nom_archivo+'"'

				writer = csv.writer(response)
				writer.writerow(['Folio','Sucursal','Fecha Emision','Nombre Usuario','Usuario','Cliente','Avaluo','Mutuo','Estatus','Fecha Vencimiento','Tipo Producto','Descripción Producto (s)'])

				for b in boletas:
					d_boleta = Det_Boleto_Empeno.objects.filter(boleta_empeno = b)					
					descripcion = ""
					for db in d_boleta:
						descripcion = descripcion + 'Descripción ' +  db.descripcion 
						
						if db.costo_kilataje != None:
							descripcion = descripcion  + ', Kilataje: ' + db.costo_kilataje.kilataje
							descripcion = descripcion  + ', Peso: ' + str(db.peso)
						
						descripcion = descripcion + '; '

					writer.writerow([b.folio,b.sucursal.sucursal,b.fecha.strftime('%Y-%m-%d'),b.usuario.username,b.usuario.first_name+' '+b.usuario.last_name,b.cliente.nombre+' '+b.cliente.apellido_p+' '+b.cliente.apellido_m,b.avaluo,b.mutuo,b.estatus.estatus,b.fecha_vencimiento.strftime('%Y-%m-%d'),b.tipo_producto.tipo_producto,descripcion])
				return response
			except:
				error = "1"
				msj_error = "No existen boletas."
				return render(request,'empenos/reportes_caja.html',locals())	
		if id_tipo_movimiento == "1000":
			try:
				boletas=Boleta_Empeno.objects.filter(fecha__range=(fecha_inicial,fecha_final)).order_by('folio')
			except:
				error="1"
				msj_error="No existen retiros en la fecha indicada."
				return render(request,'empenos/reportes_caja.html',locals())				

			try:
				nom_archivo='Rep_Det_Boletas_'+request.POST.get('fecha_inicial')+'-'+request.POST.get('fecha_final')+'.csv'
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="'+nom_archivo+'"'

				writer = csv.writer(response)

				writer.writerow(['Folio','Sucursal','Fecha Emision','Nombre Usuario','Usuario','Cliente','Avaluo','Mutuo','Estatus','Fecha Vencimiento','Tipo Producto','Descripción','Kilataje','Peso'])

				
				for b in boletas:
					
					d_boleta = Det_Boleto_Empeno.objects.filter(boleta_empeno = b)					
					descripcion = ""
					for db in d_boleta:
						
						descripcion =   db.descripcion 
						
						kilataje = ""
						peso = ""
						
						if db.costo_kilataje != None:
							kilataje = db.costo_kilataje.kilataje
							peso = str(db.peso)
						
						descripcion = descripcion + '; '
						
						writer.writerow([b.folio,b.sucursal.sucursal,b.fecha.strftime('%Y-%m-%d'),b.usuario.username,b.usuario.first_name+' '+b.usuario.last_name,b.cliente.nombre+' '+b.cliente.apellido_p+' '+b.cliente.apellido_m,b.avaluo,b.mutuo,b.estatus.estatus,b.fecha_vencimiento.strftime('%Y-%m-%d'),b.tipo_producto.tipo_producto,descripcion,kilataje,peso])

				return response

			except:
				error = "1"
				msj_error = "No existen boletas."
				return render(request,'empenos/reportes_caja.html',locals())	

		form=Reportes_Caja_Form(request.POST)
	else:
		form=Reportes_Caja_Form()

	return render(request,'empenos/reportes_caja.html',locals())	



#todos los usuarios tiene acceso.
def alta_cliente(request,id_cliente=None):
	#si no esta logueado mandamos al login
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('seguridad:login'))

	if id_cliente!=None:
		cliente=Cliente.objects.get(id=id_cliente)
	else:
		cliente=Cliente()
	
	#si el usuario y contraseña son correctas pero el perfil no es el correcto, bloquea el acceso.
	try:
		user_2=User_2.objects.get(user=request.user)
	except Exception as e:		
		form=Login_Form(request.POST)
		estatus=0
		msj="La cuenta del usuario esta incompleta."			
		return render(request,'login.html',locals())
	
	id_usuario=user_2.user.id

	c=""
	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	plazos=Plazo.objects.all()

	msj_error=""	
	try:
		#validamos si el usuaario tiene caja abierta para mostrarla en el encabezado.
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=request.user)
		c=caja.caja
	except Exception as e:
		msj_error="No cuentas con caja abierta."
		print(e)

	estatus = "2"
	if request.method=="POST":
		form=Cliente_Form(request.POST,instance=cliente)
		if form.is_valid():
			f=form.save(commit=False)
			f.usuario=request.user
			f.save()
			estatus = "1"
			
	else:
		estatus = "0"
		form=Cliente_Form(instance=cliente)
	return render(request,'empenos/alta_cliente.html',locals())

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
def consulta_abono(request):
	IP_LOCAL = settings.IP_LOCAL

	c=""
	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  	

	msj_error=""	

	try:
		costo_reimpresion=Costo_Extra.objects.get(id=1).costo
	except:
		costo_reimpresion=0



	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	if caja == None:			
		msj_error="No cuentas con caja abierta."
	else:		
		c=caja.caja
		id_caja=caja.id
		






	if request.method=="POST":
		fecha_inicial=request.POST.get("fecha_inicial")
		fecha_final=request.POST.get("fecha_final")		

		fecha_inicial=datetime.strptime(request.POST.get("fecha_inicial"), "%Y-%m-%d").date()
		fecha_final=datetime.strptime(request.POST.get("fecha_final"), "%Y-%m-%d").date()

		fecha_inicial = datetime.combine(fecha_inicial, time.min) 
		fecha_final = datetime.combine(fecha_final, time.max)  

		abonos=Abono.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=caja.sucursal)	
	else:
		pass
	sucursales = Sucursal.objects.filter(id=user_2.sucursal.id)
	form=Consulta_Abono_Form()

	return render(request,'empenos/consulta_abono.html',locals())

"""
idpermiso= 18
"""
def cancela_abono(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if not user_2.fn_tiene_acceso_a_vista(18):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	if caja != None:
		c=caja.caja
	
	msj_error = ""

	estatus = "1" 

		
	if request.method  == "POST":
		id_sucursal = request.POST.get("sucursal")
		sucursal = Sucursal.objects.get(id = int(id_sucursal))
		hoy = date.today()

		fecha_inicial = datetime.combine(hoy,time.min)
		fecha_final = datetime.combine(hoy,time.max)

		abonos=Abono.objects.filter(fecha__range=(fecha_inicial,fecha_final),sucursal=sucursal)	
	else:
		pass

	sucursales = Sucursal.objects.all()
	form=Cancela_Abono_Form()

	return render(request,'empenos/cancela_abono.html',locals())

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
def consulta_boleta(request):

	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)


	IP_LOCAL = settings.IP_LOCAL

	c=""
	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  	

	msj_error=""	

	try:
		costo_reimpresion=Costo_Extra.objects.get(id=1).costo
	except:
		costo_reimpresion=0

	try:
		#validamos si el usuaario tiene caja abierta para mostrarla en el encabezado.
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=user_2.user)
		c=caja.caja
		id_caja=caja.id
	except Exception as e:
		msj_error="No cuentas con caja abierta."
		print(e)

	if request.method=="POST":
		
		try:
			id_sucursal=request.POST.get("sucursal")	
			no_boleta=request.POST.get("boleta")
			fecha_inicial=request.POST.get("fecha_inicial")
			fecha_final=request.POST.get("fecha_final")
			estatus_boleta=request.POST.get("estatus_boleta")
			cliente=request.POST.get("cliente").upper()
			sucursal=Sucursal.objects.get(id=id_sucursal)

			if cliente!="":
				
				Cliente.fn_actualiza_nombre_completo()

				#cl = Cliente.objects.filter(nombre__contains=cliente) | Cliente.objects.filter(apellido_p__contains=cliente) | Cliente.objects.filter(apellido_m__contains=cliente)
				cl = Cliente.objects.filter(nombre_completo__contains = cliente) 
				boletas = Boleta_Empeno.objects.filter(sucursal=sucursal) & Boleta_Empeno.objects.filter(cliente__in=cl).order_by("-folio")

			elif no_boleta!="":		
				boletas=Boleta_Empeno.objects.filter(folio=int(no_boleta),sucursal=sucursal).order_by("-folio")

			elif fecha_inicial!="" and fecha_final!="":
				fecha_inicial=datetime.strptime(request.POST.get("fecha_inicial"), "%Y-%m-%d").date()
				fecha_final=datetime.strptime(request.POST.get("fecha_final"), "%Y-%m-%d").date()

				fecha_inicial=datetime.combine(fecha_inicial,time.min)
				fecha_final=datetime.combine(fecha_final,time.min)

				boletas=Boleta_Empeno.objects.filter(fecha_vencimiento__range=(fecha_inicial,fecha_final),sucursal=sucursal).order_by("-folio")
			elif estatus_boleta!="":
				estatus_boleta=Estatus_Boleta.objects.get(id=int(estatus_boleta))

				boletas=Boleta_Empeno.objects.filter(estatus=estatus_boleta,sucursal=sucursal).order_by("-folio")
		except Exception as e:
			print(e)

	else:

		print("es metodo GET")
	form=Consulta_Boleta_Form()

	sucursales=Sucursal.objects.filter(id=user_2.sucursal.id)

	return render(request,'empenos/consulta_boleta.html',locals())


#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
"""
idpermiso = 4
"""
def admin_porc_avaluo(request):
	#si regresa none, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)
	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))


	#validamos si el usuario tiene acceso a la vista.
	if not user_2.fn_tiene_acceso_a_vista(4):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))
	

	IP_LOCAL = settings.IP_LOCAL
	id_usuario=user_2.user.id

	c=""
	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	plazos=Plazo.objects.all()

	msj_error=""	
	try:
		#validamos si el usuaario tiene caja abierta para mostrarla en el encabezado.
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=request.user)
		print(caja.sucursal)
		c=caja.caja
	except Exception as e:
		msj_error="No cuentas con caja abierta."
		print(e)

	permiso="1"#si tiene permiso para entrar a esta opcion.
		

	error="0"
	if request.method=="POST":
		if permiso=="1":
			form=Porcentaje_Sobre_Avaluo_Form(request.POST)
			if decimal.Decimal(request.POST.get("porcentaje"))>decimal.Decimal(100) or decimal.Decimal(request.POST.get("porcentaje"))<decimal.Decimal(0):
				error="1"
				porcentaje=Porcentaje_Sobre_Avaluo.objects.all()
				porc=0
				porc_apartado=0
				for x in porcentaje:
					porc=x.porcentaje
					porc_apartado=x.porcentaje_apartado
				form=Porcentaje_Sobre_Avaluo_Form()				
				return render(request,'empenos/admin_porc_avaluo.html',locals())
			if form.is_valid():
				try:
					Porcentaje_Sobre_Avaluo.objects.all().delete()
				except:
					print("no hay porcentaje registrado")
				form.save()
				porcentaje=Porcentaje_Sobre_Avaluo.objects.all()
				porc=0
				porc_apartado=0
				for x in porcentaje:
					porc=x.porcentaje
					porc_apartado=x.porcentaje_apartado
				error="0"
				return render(request,'empenos/admin_porc_avaluo.html',locals())
		else:
			error="1"
			form=Porcentaje_Sobre_Avaluo_Form()
			print("No hace algo ya que no tiene permiso.")
	else:
		error="2"
		porcentaje=Porcentaje_Sobre_Avaluo.objects.all()

		porc=0
		porc_apartado=0
		for x in porcentaje:
			porc=x.porcentaje
			porc_apartado=x.porcentaje_apartado

		form=Porcentaje_Sobre_Avaluo_Form()

	return render(request,'empenos/admin_porc_avaluo.html',locals())

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
@transaction.atomic
def nvo_empeno(request):	
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	IP_LOCAL = settings.IP_LOCAL

	#el usuario real que hace el empeño
	id_usuario = request.user.id

	c=""
	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	plazos = Plazo.objects.all()

	msj_error=""	
	try:
		#validamos si el usuaario virtual tiene caja abierta
		caja = Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=user_2.user)
		c = caja.caja
	except Exception as e:
		msj_error = "La sucursal no ha aperturado caja."
		print(e)
		form = Nuevo_Empeno_Form()
		empeno_exitoso = "2"
		return render(request,'empenos/nvo_empeno.html',locals())

	id_sucursal = caja.sucursal.id

	sucursal = caja.sucursal

	#un 1 indica que no tenemos registrado el porcentaje de mutuo.
	error_porcentaje_mutuo = "0"	
	try:
		porcentaje_mutuo_oro = decimal.Decimal(sucursal.fn_consulta_porcentaje_mutuo().porcentaje_oro)/decimal.Decimal(100.00)
		porcentaje_mutuo_plata = decimal.Decimal(sucursal.fn_consulta_porcentaje_mutuo().porcentaje_plata)/decimal.Decimal(100.00)
		porcentaje_articulos_varios = decimal.Decimal(sucursal.fn_consulta_porcentaje_mutuo().porcentaje_articulos_varios)/decimal.Decimal(100.00)
		print(porcentaje_articulos_varios)
	except Exception as e:
		print(e)
		error_porcentaje_mutuo = "1"
		form=Nuevo_Empeno_Form()
		empeno_exitoso="2"
		return render(request,'empenos/nvo_empeno.html',locals())	

	#un 1 indica que no tenemos registrado el porcentaje de interes del mutuo
	error_porcentaje_interes = "0"

	#validamos que tenga configurado el porcentaje para interes del refrendo.
	try:
		Configuracion_Interes_Empeno.objects.get(sucursal = sucursal)
	except Exception as e:
		print(e)
		error_porcentaje_interes = "1"
		form=Nuevo_Empeno_Form()
		empeno_exitoso="2"
		return render(request,'empenos/nvo_empeno.html',locals())


	#buscamos el tipo de movimiento para boleta.
	tm=Tipo_Movimiento.objects.get(id=4)

	empeno_exitoso="0"

	if request.method=="POST":
		try:
			hoy = datetime.now()#fecha actual


			#calculamos la fecha de vemcimiento para 4 semanas
			if int(request.POST.get("plazo"))==2:
				dias = timedelta(days=28)		                
				fecha_vencimiento=datetime.combine(hoy+dias, time.min)
				fecha_vencimiento_real=fecha_vencimiento
				fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

			elif int(request.POST.get("plazo"))==1:
				dias = timedelta(days=1)
				#fecha_vencimiento=hoy+dias
				fecha_vencimiento=datetime.combine(hoy+dias, time.min)
				fecha_vencimiento_real=fecha_vencimiento
				#validmoas que la fecha de vencimiento no sea de azueto
				fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)
			elif int(request.POST.get("plazo"))==3:							
				fecha_vencimiento=datetime.combine(fn_add_months(hoy,1), time.min)	
				fecha_vencimiento_real=fecha_vencimiento
				#validmoas que la fecha de vencimiento no sea de azueto
				fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

			cliente=Cliente.objects.get(id=int(request.POST.get("cliente")))
			refrendo=Tipo_Pago.objects.get(id=1)
			oro=Tipo_Producto.objects.get(id=1)			
			plazo=Plazo.objects.get(id=int(request.POST.get("plazo")))

			#buscamos los productos de oro que estan en la cotizacion y que corresponden al usuario.
			poro=Empenos_Temporal.objects.filter(tipo_producto=oro,usuario=request.user)
			
			if poro.exists():
				#creamos el folio para la boleta de oro
				folio=fn_folios(tm,user_2.sucursal)			
				str_folio=fn_str_clave(folio)

				avaluo=0
				mutuo=0

				#acumulamos el avaluo y el oro
				for x in poro:
					avaluo = avaluo + x.avaluo
					mutuo = mutuo + x.mutuo

				boleta = Boleta_Empeno()
				boleta.folio = str_folio
				boleta.tipo_producto = oro
				boleta.caja = caja #por medio de la caja obtenemos el usuario virtual y la sucursal
				boleta.usuario = request.user #con el usuario nos damos cuenta de quien realmente hizo el empeño
				boleta.avaluo = avaluo
				boleta.mutuo = mutuo
				boleta.fecha = timezone.now()
				boleta.fecha_vencimiento = fecha_vencimiento
				boleta.cliente = cliente
				boleta.nombre_cotitular = request.POST.get("nombre_cotitular")
				boleta.apellido_p_cotitular = request.POST.get("apellido_paterno")
				boleta.apellido_m_cotitular = request.POST.get("apellido_materno")
				boleta.plazo = plazo
				boleta.sucursal = caja.sucursal
				boleta.mutuo_original = mutuo
				boleta.fecha_vencimiento_real = fecha_vencimiento_real

				#almacenamos los porcentajes para el interes por si con el tiempo cambian
				#calcular los nuevos refrendos a como esaban al generar la boleta.
				boleta.interes = sucursal.fn_get_interes(1)#
				boleta.almacenaje = sucursal.fn_get_almacenaje(1)
				boleta.iva = sucursal.fn_get_iva(1)

				boleta.save()


				#llenamos la tabla de pagos.				
				if int(request.POST.get("plazo"))==2:#semanal
					days = timedelta(days=7)
					
					fecha_vencimiento = datetime.combine(hoy+days, time.min) 
					fecha_vencimiento_real=fecha_vencimiento
					fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

					ref = sucursal.fn_calcula_refrendo(boleta.mutuo,1)

					almacenaje_semanal=ref[0]["almacenaje"]/4
					interes_semanal=(ref[0]["interes"])/4
					iva_semanal=ref[0]["iva"]/4
					importe_semanal=ref[0]["refrendo"]/4#(almacenaje_semanal+interes_semanal+iva_semanal)

					if round(importe_semanal)==0:
						importe_semanal=1
					else:
						importe_semanal=round(importe_semanal)


					Pagos.objects.create(tipo_pago=refrendo,boleta=boleta,fecha_vencimiento=fecha_vencimiento,importe=importe_semanal,almacenaje=almacenaje_semanal,interes=interes_semanal,iva=iva_semanal,fecha_vencimiento_real=fecha_vencimiento_real)

					days = timedelta(days=14)					
					fecha_vencimiento = datetime.combine(hoy+days, time.min) 
					fecha_vencimiento_real=fecha_vencimiento
					fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)
					Pagos.objects.create(tipo_pago=refrendo,boleta=boleta,fecha_vencimiento=fecha_vencimiento,importe=importe_semanal,almacenaje=almacenaje_semanal,interes=interes_semanal,iva=iva_semanal,fecha_vencimiento_real=fecha_vencimiento_real)

					days = timedelta(days=21)					

					fecha_vencimiento = datetime.combine(hoy+days, time.min) 
					fecha_vencimiento_real=fecha_vencimiento
					fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

					Pagos.objects.create(tipo_pago=refrendo,boleta=boleta,fecha_vencimiento=fecha_vencimiento,importe=importe_semanal,almacenaje=almacenaje_semanal,interes=interes_semanal,iva=iva_semanal,fecha_vencimiento_real=fecha_vencimiento_real)

					days = timedelta(days=28)					
					fecha_vencimiento = datetime.combine(hoy+days, time.min) 
					fecha_vencimiento_real=fecha_vencimiento
					fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)
					Pagos.objects.create(tipo_pago=refrendo,boleta=boleta,fecha_vencimiento=fecha_vencimiento,importe=importe_semanal,almacenaje=almacenaje_semanal,interes=interes_semanal,iva=iva_semanal,fecha_vencimiento_real=fecha_vencimiento_real)

					boleta.refrendo=math.ceil((importe_semanal*4.00))
					boleta.save()
				elif int(request.POST.get("plazo"))==1:#diario
					print("En diarios no se calcula el pago ya que se asume que es para venta.")
				elif int(request.POST.get("plazo"))==3:#mensual
					ref = sucursal.fn_calcula_refrendo(boleta.mutuo,1)
					#ref=fn_calcula_refrendo(boleta.mutuo,boleta.tipo_producto.id)

					pago=Pagos()
					pago.tipo_pago=refrendo
					pago.boleta=boleta
					pago.fecha_vencimiento=fecha_vencimiento
					pago.importe=round(ref[0]["refrendo"])
					pago.almacenaje=ref[0]["almacenaje"]
					pago.interes=ref[0]["interes"]
					pago.iva=ref[0]["iva"]					
					pago.fecha_vencimiento_real=boleta.fecha_vencimiento_real
					pago.save()


					boleta.refrendo=round(ref[0]["refrendo"])
					boleta.save()

					fn_pago_parcial(boleta,hoy,round(ref[0]["refrendo"]),pago)



				
				#almcenamos la boleta para imprimirla posteriormente
				Imprimir_Boletas.objects.create(usuario=request.user,boleta=boleta)

				#recorremos cada producto de oro para agregar al detalle de la boleta.		
				for x in poro:
					je=Joyeria_Empenos_Temporal.objects.get(empeno_temporal=x)
					db=Det_Boleto_Empeno()
					db.boleta_empeno=boleta
					db.tipo_producto=x.tipo_producto
					db.linea=x.linea
					db.sub_linea=x.sub_linea
					db.marca=x.marca
					db.descripcion=x.descripcion
					db.avaluo=x.avaluo
					db.mutuo_sugerido=x.mutuo_sugerido
					db.mutuo=x.mutuo
					db.costo_kilataje=je.costo_kilataje
					db.peso=je.peso
					db.save()

				for x in poro:
					Joyeria_Empenos_Temporal.objects.get(empeno_temporal=x).delete()
				#si se guardo correctamente, borramos la cotizacino temporal.
				Empenos_Temporal.objects.filter(tipo_producto=oro,usuario=request.user).delete()

			#***********************************************************************************************************************************
			#***********************************************************************************************************************************
			#creamosla boleta para plata
			plata=Tipo_Producto.objects.get(id=2)

			#buscamos los productos de oro del actual afiliado.
			tplata=Empenos_Temporal.objects.filter(tipo_producto=plata,usuario=request.user)

			if tplata.exists():

				#creamos el folio para la boleta de plata
				folio=fn_folios(tm,user_2.sucursal)			
				str_folio=fn_str_clave(folio)

				avaluo=0
				mutuo=0
				for x in tplata:
					avaluo=avaluo+x.avaluo
					mutuo=mutuo+x.mutuo
				boleta=Boleta_Empeno()
				boleta.folio=str_folio
				boleta.tipo_producto=plata
				boleta.caja=caja
				boleta.usuario=request.user
				boleta.avaluo=avaluo
				boleta.mutuo=mutuo
				boleta.fecha=timezone.now()
				boleta.fecha_vencimiento=fecha_vencimiento
				boleta.cliente=cliente
				boleta.nombre_cotitular=request.POST.get("nombre_cotitular")
				boleta.apellido_p_cotitular=request.POST.get("apellido_paterno")
				boleta.apellido_m_cotitular=request.POST.get("apellido_materno")
				boleta.plazo=plazo
				boleta.sucursal=caja.sucursal
				boleta.mutuo_original=mutuo
				boleta.fecha_vencimiento_real=fecha_vencimiento_real

				#almacenamos los porcentajes para el interes por si con el tiempo cambian
				#calcular los nuevos refrendos a como esaban al generar la boleta.
				boleta.interes = sucursal.fn_get_interes(2)#
				boleta.almacenaje = sucursal.fn_get_almacenaje(2)
				boleta.iva = sucursal.fn_get_iva(2)


				boleta.save()

				#almcenamos la boleta para imprimirla posteriormente
				Imprimir_Boletas.objects.create(usuario=request.user,boleta=boleta)

				#llenamos la tabla de pagos.				
				if int(request.POST.get("plazo"))==2:#semanal
					days = timedelta(days=7)
					
					fecha_vencimiento = datetime.combine(hoy+days, time.min) 
					fecha_vencimiento_real=fecha_vencimiento
					fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

					ref = sucursal.fn_calcula_refrendo(boleta.mutuo,2)

					almacenaje_semanal=ref[0]["almacenaje"]/4
					interes_semanal=(ref[0]["interes"])/4
					iva_semanal=ref[0]["iva"]/4
					importe_semanal=ref[0]["refrendo"]/4#(almacenaje_semanal+interes_semanal+iva_semanal)


					if round(importe_semanal)==0:
						importe_semanal=1
					else:
						importe_semanal=round(importe_semanal)

					Pagos.objects.create(tipo_pago=refrendo,boleta=boleta,fecha_vencimiento=fecha_vencimiento,importe=importe_semanal,almacenaje=almacenaje_semanal,interes=interes_semanal,iva=iva_semanal,fecha_vencimiento_real=fecha_vencimiento_real)

					days = timedelta(days=14)					
					fecha_vencimiento = datetime.combine(hoy+days, time.min) 
					fecha_vencimiento_real=fecha_vencimiento
					fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)
					Pagos.objects.create(tipo_pago=refrendo,boleta=boleta,fecha_vencimiento=fecha_vencimiento,importe=importe_semanal,almacenaje=almacenaje_semanal,interes=interes_semanal,iva=iva_semanal,fecha_vencimiento_real=fecha_vencimiento_real)

					days = timedelta(days=21)					
					fecha_vencimiento = datetime.combine(hoy+days, time.min) 
					fecha_vencimiento_real=fecha_vencimiento
					fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)
					Pagos.objects.create(tipo_pago=refrendo,boleta=boleta,fecha_vencimiento=fecha_vencimiento,importe=importe_semanal,almacenaje=almacenaje_semanal,interes=interes_semanal,iva=iva_semanal,fecha_vencimiento_real=fecha_vencimiento_real)

					days = timedelta(days=28)					
					fecha_vencimiento = datetime.combine(hoy+days, time.min) 
					fecha_vencimiento_real=fecha_vencimiento
					fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)
					Pagos.objects.create(tipo_pago=refrendo,boleta=boleta,fecha_vencimiento=fecha_vencimiento,importe=importe_semanal,almacenaje=almacenaje_semanal,interes=interes_semanal,iva=iva_semanal,fecha_vencimiento_real=fecha_vencimiento_real)

					boleta.refrendo=math.ceil((importe_semanal*4.00))
					boleta.save()
				elif int(request.POST.get("plazo"))==1:#diario
					print("aun esta listo")
				elif int(request.POST.get("plazo"))==3:#mensual
					#ref=fn_calcula_refrendo(boleta.mutuo,boleta.tipo_producto.id)				
					ref = sucursal.fn_calcula_refrendo(boleta.mutuo,2)

					pago=Pagos()
					pago.tipo_pago=refrendo
					pago.boleta=boleta
					pago.fecha_vencimiento=fecha_vencimiento
					pago.importe=round(ref[0]["refrendo"])
					pago.almacenaje=ref[0]["almacenaje"]
					pago.interes=ref[0]["interes"]
					pago.iva=ref[0]["iva"]
					pago.fecha_vencimiento_real=boleta.fecha_vencimiento_real
					pago.save()

					boleta.refrendo=round(ref[0]["refrendo"])
					boleta.save()

					fn_pago_parcial(boleta,hoy,round(ref[0]["refrendo"]),pago)

				#recorremos cada producto de plata para agregar al detalle de la boleta.		
				for x in tplata:
					je=Joyeria_Empenos_Temporal.objects.get(empeno_temporal=x)
					db=Det_Boleto_Empeno()
					db.boleta_empeno=boleta
					db.tipo_producto=x.tipo_producto
					db.linea=x.linea
					db.sub_linea=x.sub_linea
					db.marca=x.marca
					db.descripcion=x.descripcion
					db.avaluo=x.avaluo
					db.mutuo_sugerido=x.mutuo_sugerido
					db.mutuo=x.mutuo
					db.costo_kilataje=je.costo_kilataje
					db.peso=je.peso
					db.save()

				for x in tplata:
					Joyeria_Empenos_Temporal.objects.get(empeno_temporal=x).delete()
				#si se guardo correctamente, borramos la cotizacino temporal de la plata.
				Empenos_Temporal.objects.filter(tipo_producto=plata,usuario=request.user).delete()

			#creamosla boleta para plata
			varios=Tipo_Producto.objects.get(id=3)

			#buscamos los productos de oro del actual afiliado.
			tvarios=Empenos_Temporal.objects.filter(tipo_producto=varios,usuario=request.user)


			if tvarios.exists():
				#para productos varios no se agrupan los productos, se crea una boleta para cada producto.
				for x in tvarios:

					#creamos el folio para cada una de las boletas de varios.
					folio=fn_folios(tm,user_2.sucursal)			
					str_folio=fn_str_clave(folio)

					boleta=Boleta_Empeno()
					boleta.folio=str_folio
					boleta.tipo_producto=varios
					boleta.caja=caja
					boleta.usuario=request.user
					boleta.avaluo=x.avaluo
					boleta.mutuo=x.mutuo
					boleta.fecha=timezone.now()
					boleta.fecha_vencimiento=fecha_vencimiento
					boleta.cliente=cliente
					boleta.nombre_cotitular=request.POST.get("nombre_cotitular")
					boleta.apellido_p_cotitular=request.POST.get("apellido_paterno")
					boleta.apellido_m_cotitular=request.POST.get("apellido_materno")
					boleta.plazo=plazo		
					boleta.sucursal=caja.sucursal		
					boleta.mutuo_original=x.mutuo
					boleta.fecha_vencimiento_real=fecha_vencimiento_real


					#almacenamos los porcentajes para el interes por si con el tiempo cambian
					#calcular los nuevos refrendos a como esaban al generar la boleta.
					boleta.interes = sucursal.fn_get_interes(3)#
					boleta.almacenaje = sucursal.fn_get_almacenaje(3)
					boleta.iva = sucursal.fn_get_iva(3)

					boleta.save()

					#llenamos la tabla de pagos.				
					if int(request.POST.get("plazo"))==2:#semanal
						days = timedelta(days=7)
						
						fecha_vencimiento = datetime.combine(hoy+days, time.min) 
						fecha_vencimiento_real=fecha_vencimiento
						fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

						ref = sucursal.fn_calcula_refrendo(boleta.mutuo,3)

						almacenaje_semanal=ref[0]["almacenaje"]/4
						interes_semanal=(ref[0]["interes"])/4
						iva_semanal=ref[0]["iva"]/4
						importe_semanal=ref[0]["refrendo"]/4#(almacenaje_semanal+interes_semanal+iva_semanal)

						if round(importe_semanal)==0:
							importe_semanal=1
						else:
							importe_semanal=round(importe_semanal)


						Pagos.objects.create(tipo_pago=refrendo,boleta=boleta,fecha_vencimiento=fecha_vencimiento,importe=importe_semanal,almacenaje=almacenaje_semanal,interes=interes_semanal,iva=iva_semanal,fecha_vencimiento_real=fecha_vencimiento_real)

						days = timedelta(days=14)					
						fecha_vencimiento = datetime.combine(hoy+days, time.min) 
						fecha_vencimiento_real=fecha_vencimiento
						fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)
						Pagos.objects.create(tipo_pago=refrendo,boleta=boleta,fecha_vencimiento=fecha_vencimiento,importe=importe_semanal,almacenaje=almacenaje_semanal,interes=interes_semanal,iva=iva_semanal,fecha_vencimiento_real=fecha_vencimiento_real)

						days = timedelta(days=21)					
						fecha_vencimiento = datetime.combine(hoy+days, time.min) 
						fecha_vencimiento_real=fecha_vencimiento
						fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)
						Pagos.objects.create(tipo_pago=refrendo,boleta=boleta,fecha_vencimiento=fecha_vencimiento,importe=importe_semanal,almacenaje=almacenaje_semanal,interes=interes_semanal,iva=iva_semanal,fecha_vencimiento_real=fecha_vencimiento_real)

						days = timedelta(days=28)					
						fecha_vencimiento = datetime.combine(hoy+days, time.min) 
						fecha_vencimiento_real=fecha_vencimiento
						fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)
						Pagos.objects.create(tipo_pago=refrendo,boleta=boleta,fecha_vencimiento=fecha_vencimiento,importe=importe_semanal,almacenaje=almacenaje_semanal,interes=interes_semanal,iva=iva_semanal,fecha_vencimiento_real=fecha_vencimiento_real)

						boleta.refrendo=math.ceil((importe_semanal*4.00))
						boleta.save()

					elif int(request.POST.get("plazo"))==1:#diario
						print("aun esta listo")
					elif int(request.POST.get("plazo"))==3:#mensual

						ref = sucursal.fn_calcula_refrendo(boleta.mutuo,3)

						pago=Pagos()
						pago.tipo_pago=refrendo
						pago.boleta=boleta
						pago.fecha_vencimiento=fecha_vencimiento
						pago.importe=round(ref[0]["refrendo"])
						pago.almacenaje=ref[0]["almacenaje"]
						pago.interes=ref[0]["interes"]
						pago.iva=ref[0]["iva"]

						pago.fecha_vencimiento_real=boleta.fecha_vencimiento_real

						pago.save()
						
						boleta.refrendo=round(ref[0]["refrendo"])
						boleta.save()

						fn_pago_parcial(boleta,hoy,round(ref[0]["refrendo"]),pago)

					#almcenamos la boleta para imprimirla posteriormente
					Imprimir_Boletas.objects.create(usuario=request.user,boleta=boleta)

					db=Det_Boleto_Empeno()
					db.boleta_empeno=boleta
					db.tipo_producto=x.tipo_producto
					db.linea=x.linea
					db.sub_linea=x.sub_linea
					db.marca=x.marca
					db.descripcion=x.descripcion
					db.avaluo=x.avaluo
					db.mutuo_sugerido=x.mutuo_sugerido
					db.mutuo=x.mutuo
					db.observaciones=x.observaciones

					#db.costo_kilataje=je.costo_kilataje
					#db.peso=je.peso
					db.save()

				#si se guardo correctamente, borramos la cotizacino temporal de articulos varios.
				Empenos_Temporal.objects.filter(tipo_producto=varios,usuario=request.user).delete()
			empeno_exitoso="1"
			
		except Exception as e:
			print(e)
			empeno_exitoso="0"

		form=Nuevo_Empeno_Form()
	else:
		form=Nuevo_Empeno_Form()
		empeno_exitoso="2"
	return render(request,'empenos/nvo_empeno.html',locals())		


#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
def admin_comisionpg(request):
	#si regresa nonem, es porque el usuario no esta logueado.
	user_2 = User_2.fn_is_logueado(request.user)

	if user_2 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	if not user_2.fn_tiene_acceso_a_vista(24):
		return HttpResponseRedirect(reverse('seguridad:sin_permiso_de_acceso'))


	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()
	if caja == None:
		c=""
	else:
		c=caja.caja	

	estatus = "1"
	if request.method == "POST":		
		try:
			pcp = Porcentaje_Comision_PG.objects.get(id = 1)			
		except:
			pcp = Porcentaje_Comision_PG()
		try:	
			pcp.porcentaje = request.POST.get("porcentaje")
			pcp.usuario = request.user
			pcp.save()
			estatus = "2"
		except:
			estatus = "0"

	form = Porcenaje_Comisionpg_Form()
	try:
		pcp_inf = Porcentaje_Comision_PG.objects.get(id = 1)
		valor = pcp_inf.porcentaje
	except:
		valor = 0.00

	

	return render(request,'empenos/admin_comisionpg.html',locals())

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************


#Se aplican refrendos para cuantro semanas.
def refrendo(request,id_boleta):

	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	
	
	msj_error = ""

	#el estatus 1 indica que todo esta ok, 
	#el estatus 0 indica que se presento un error. el error debe venir acompalñado de una leyenda en la variable msj_error
	estatus = "1" 

	if caja == None:		
		msj_error="No cuentas con caja abierta."
		estatus = "0"
		return render(request,'empenos/refrendo_semanal.html',locals())

	c=caja.caja

	#buscamos la boleta a refrendar.
	boleta=Boleta_Empeno.objects.get(id=int(id_boleta))
 
	det_boleta = Det_Boleto_Empeno.objects.filter(boleta_empeno = boleta)
	#validamos si la boleta acepta refrendos o no.
	if not boleta.fn_acepta_refrendo():
		msj_error = "La boleta no permite refrendos."
		estatus = "0"
		return render(request,'empenos/refrendo_semanal.html',locals())

	min_semanas_refrendar = boleta.fn_get_min_y_max_semanas_a_pagar()["min_semanas_a_refrendar"]
	max_semanas_refrendar = boleta.fn_get_min_y_max_semanas_a_pagar()["max_semanas_a_refrendar"]

	semanas_vencidas = max_semanas_refrendar - 1
	if semanas_vencidas < 0:
		semanas_vencidas = 0 
	#obtenemos el importe de una comision pg
	est_comisionpg=Tipo_Pago.objects.get(id=2)	
	
	importe_refrendo = str(round(float(Pagos.objects.filter(boleta = boleta,pagado = "N").exclude(tipo_pago__id = 2).aggregate(Max("importe"))["importe__max"])))+".00"

	importe_compg = float(boleta.fn_get_comision_pg())
	
	dias_vencido = boleta.fn_get_dias_vencida()

	return render(request,"empenos/refrendo_semanal.html",locals())








"""

	id_usuario=user_2.user.id

	IP_LOCAL=settings.IP_LOCAL

	c=""
	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	plazos=Plazo.objects.all()

	msj_error=""	
	try:
		#validamos si el usuaario tiene caja abierta para mostrarla en el encabezado.
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=request.user)
		c=caja.caja
	except Exception as e:
		msj_error="No cuentas con caja abierta."
		print(e)

	hoy=datetime.now()#fecha actual
	hoy=datetime.combine(hoy, time.min)

	username=request.user.username

	boleta=Boleta_Empeno.objects.get(id=int(id_boleta))

	dias_empeno=abs((hoy-boleta.fecha).days)
	importe_refrendo=math.ceil(fn_calcula_saldo_refrendo(boleta,hoy))
	importe_refrendopg=math.ceil(fn_saldo_refrendopg(boleta))
	importe_comisionpg=math.ceil(fn_saldo_comisionpg(boleta))

	pag_vencido=Pagos.objects.filter(boleta=boleta,vencido="S",pagado="N").exclude(tipo_pago=est_comisionpg).aggregate(Sum("importe"))

	if pag_vencido["importe__sum"]==None:
		importe_saldo_vencido=0.00
	else:
		importe_saldo_vencido=pag_vencido["importe__sum"]


	importe_refrendo_total=importe_refrendo+importe_refrendopg

	pago_obligatorio=importe_refrendopg+importe_comisionpg

	refrendo=Tipo_Pago.objects.get(id=1)

	pagos=Pagos.objects.filter(boleta=boleta,pagado="N",tipo_pago=refrendo)

	monto_minimo_refrendo=0.00

	for x in pagos:		
		monto_minimo_refrendo=x.importe


	compg=Pagos.objects.filter(boleta=boleta,tipo_pago=est_comisionpg,pagado="N")
	minimo_pg=0
	for x in compg:
		minimo_pg=x.importe

	if minimo_pg>0:#si es cero, esque la boleta no esta vencida.
		dias_vencido=abs((hoy-boleta.fecha_vencimiento).days)

		#calculamos el descuento que se le puede hacer por ponerse al corriente
		if dias_vencido<=3:
			minimo_pg=minimo_pg*dias_vencido
		else:
			minimo_pg=0



	abono_aplicado="2"
	if request.method=="POST":
		try:
			importe_abono=int(float(request.POST.get("importe_abono")))
			desc_pg=int(float(request.POST.get("desc_pg")))

			

			#si es apto para el descuento
			#y ya cubrio todo el saldo vencido

			#if minimo_pg!=0 and importe_abono>=importe_saldo_vencido:
			if desc_pg==1:
				#borramos las comisiones pg
				Pagos.objects.filter(boleta=boleta,pagado="N",tipo_pago=est_comisionpg).delete()


		
			fn_aplica_refrendo(request.user,importe_abono,caja,boleta,0)
			abono_aplicado="1"
		except Exception as e:
			abono_aplicado="0"
			print(e)
			print("error al aplicar el abono")


	form=Refrendo_Form()	
	return render(request,'empenos/refrendo.html',locals())
"""
#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
@transaction.atomic
def refrendo_plazo_mensual(request,id_boleta):	
	#si regresa none, es porque el usuario no esta logueado.
	user_2_1 = User_2.fn_is_logueado(request.user)
	if user_2_1 == None:
		return HttpResponseRedirect(reverse('seguridad:login'))

	#obtenemos el usuario virtual de la sucursal.
	#ya que sobre este usuario se registran los ingresos.
	user_2 = User_2.objects.get(user = user_2_1.sucursal.usuario_virtual)

	#validamos si el usuario tiene caja abierta
	caja = user_2.fn_tiene_caja_abierta()

	
	
	msj_error = ""

	#el estatus 1 indica que todo esta ok, 
	#el estatus 0 indica que se presento un error. el error debe venir acompalñado de una leyenda en la variable msj_error
	

	if caja == None:		
		msj_error="No cuentas con caja abierta."
		
		return render(request,'empenos/refrendo_semanal.html',locals())

	c=caja.caja

	id_usuario=user_2.user.id

	IP_LOCAL=settings.IP_LOCAL

	c=""
	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	plazos=Plazo.objects.all()

	msj_error=""	


	hoy=datetime.now()#fecha actual
	hoy=datetime.combine(hoy, time.min)

	boleta=Boleta_Empeno.objects.get(id=int(id_boleta))

	est_comisionpg=Tipo_Pago.objects.get(id=2)	
	est_refrendo=Tipo_Pago.objects.get(id=1)		
	est_refrendopg=Tipo_Pago.objects.get(id=3)

	ref_no_pagados=(Pagos.objects.filter(tipo_pago=est_refrendo,pagado="N",boleta=boleta) | Pagos.objects.filter(tipo_pago=est_refrendopg,pagado="N",boleta=boleta)).aggregate(Sum("importe"))
	
	if ref_no_pagados["importe__sum"]==None:
		importe_refrendo_total=0.00
	else:
		importe_refrendo_total=ref_no_pagados["importe__sum"]

	ref_com_pg=Pagos.objects.filter(tipo_pago=est_comisionpg,pagado="N",boleta=boleta).aggregate(Sum("importe"))
	if ref_com_pg["importe__sum"]==None:
		importe_comision_pg=0.00
	else:
		importe_comision_pg=ref_com_pg["importe__sum"]
	
	#obtenemos todos los periodos que no han sido pagados.
	periodos=Periodo.objects.filter(boleta=boleta,pagado="N")
	importe_max_periodo=Periodo.objects.filter(boleta=boleta,pagado="N").aggregate(Max("importe"))

	importe_periodo=0.00
	if importe_max_periodo["importe__max"]==None:
		importe_periodo=0.00
	else:
		importe_periodo=importe_max_periodo["importe__max"]

	

	contador=0

	lista_periodo=[]
	
	for x in periodos:
		contador=contador+1
		lista_periodo.append({"id":contador,"txt":str(contador)+" Periodo Parcial "})	


	nota_activar_boleta=""
	if contador>4:
		nota_activar_boleta="Para activar la boleta, debes pagar al menos "+str(contador-4)	+" boleta(s)."

	username=request.user.username

	#calculamos si va a pagar comision o no
	# si se pone al corriente dentro de los primeros tres dias despues de vencimiento, no se paga refrendo PG
	dias_vencido=abs((hoy-boleta.fecha_vencimiento).days)

	if dias_vencido<0:
		dias_vencido=0


	aplicamos_descuento=0
	if dias_vencido<=3:
		aplicamos_descuento=1

	cont_periodos_vencidos=int(Periodo.objects.filter(pagado="N",vencido="S",boleta=boleta).count())

	abono_aplicado="2"
	#si es post aplicamos el refrendo.
	if request.method=="POST":
		try:
			
			if request.POST.get("id_periodos")==None:
				periodos_pagados=int(0)
			else:
				periodos_pagados=int(request.POST.get("id_periodos"))

			total_refrendo=int(round(decimal.Decimal(request.POST.get("total_refrendo"))))
			

			if aplicamos_descuento==1:
				if periodos_pagados>=cont_periodos_vencidos:
					#total_refrendo=total_refrendo+importe_comision_pg
					Pagos.objects.filter(tipo_pago=est_comisionpg,pagado="N",boleta=boleta).delete()

			tm=Tipo_Movimiento.objects.get(id=5)		
			folio=fn_folios(tm,boleta.sucursal)
			

			abono=Abono()
			abono.usuario=request.user
			abono.importe=total_refrendo
			abono.caja=caja
			abono.boleta=boleta
			abono.folio=folio
			abono.tipo_movimiento=tm
			abono.sucursal=boleta.sucursal

			abono.save()

			Imprime_Abono.objects.filter(usuario=request.user).delete()

			Imprime_Abono.objects.create(usuario=request.user,abono=abono)

			#buscamos las comisiones pg para saldarlas.
			com_pg=Pagos.objects.filter(tipo_pago=est_comisionpg,pagado="N",boleta=boleta)

			for c in com_pg:
				c.pagado="S"
				c.fecha_pago=timezone.now()
				c.save()

				#creamos la relacion entre el abono y los pagos
				rel=Rel_Abono_Pago()
				rel.abono=abono
				rel.pago=c
				rel.save()

				total_refrendo=total_refrendo-c.importe

			periodos=Periodo.objects.filter(boleta=boleta,pagado="N").order_by("fecha_vencimiento")		
			mutuo=boleta.mutuo
			fecha_vencimiento=boleta.fecha_vencimiento
			#liquidamos los periodos.
			for p in periodos:

				if int(total_refrendo)>=int(p.importe):
					p.pagado="S"
					p.fecha_pago=timezone.now()
					p.save()

					rap=Rel_Abono_Periodo()
					rap.abono=abono
					rap.periodo=p
					rap.save()

					#si el pag al que corresponde el periodo  saldado, ya no cuenta con periodos sin pagar, se marca como pagado.
					per_pago=Periodo.objects.filter(pago=p.pago,pagado="N").count()
					if per_pago==0:
						p.pago.pagado="S"
						p.pago.fecha_pago=timezone.now()						
						p.pago.save()

					#se calcula la nueva fecha de vencimiento.
					fecha_vencimiento=fn_add_months(p.fecha_vencimiento,1)

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

					#total_refrendo=int(total_refrendo)-int(p.importe)
			
					total_refrendo=decimal.Decimal(total_refrendo)-decimal.Decimal(p.importe)
		
			total_refrendo=int(round(total_refrendo))

			cont_periodos_vencidos=Periodo.objects.filter(boleta=boleta,pagado="N").count()

			#si el total_refrendo es mayor a cero
			# y ya no tiene periodos sin pagar, abonamos a capital.
			if int(cont_periodos_vencidos)==0:
				if int(total_refrendo)>0 :			
					mutuo=mutuo-int(total_refrendo)
					if mutuo<=0:
						mutuo=0
					rel_cap=Rel_Abono_Capital()
					rel_cap.boleta=boleta
					rel_cap.abono=abono
					rel_cap.importe=int(total_refrendo)
					rel_cap.capital_restante=mutuo
					rel_cap.save()

			#por los redondeos aplicados en el formulario, puede darse el caso de que el mutuo termine con importe menor a cero.
			if mutuo<=0:
				mutuo=0

				desempenada=Estatus_Boleta.objects.get(id=4)
				boleta.estatus=desempenada
				boleta.mutuo=0
				boleta.refrendo=0
				boleta.save()

			fecha_vencimiento=datetime.combine(fecha_vencimiento, time.min)

			#validamos que la fecha de vencimiento no sea dia de asueto.
			fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

			hoy=datetime.now()#fecha actual
			hoy=datetime.combine(hoy, time.min)

			if mutuo>0:
				if fecha_vencimiento<hoy:
					
					estatus=Estatus_Boleta.objects.get(id=3)	
				else:
				
					estatus=Estatus_Boleta.objects.get(id=1)	
				boleta.estatus=estatus

			#actualizamos la fecha de vencimiento de la boleta.		
			boleta.fecha_vencimiento=fecha_vencimiento
			boleta.mutuo=mutuo
			boleta.save()
			abono_aplicado="1"
		except Exception as e:
			print(e)
			abono_aplicado="0"



	form=Refrendo_Mensual_Form()

	return render(request,'empenos/refrendo_periodo_mensual.html',locals())



#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

def re_imprimir_venta(request,id_venta):
	venta=Venta_Granel.objects.get(id=id_venta)
	Imprime_Venta_Granel.objects.filter(usuario=request.user).delete()
	Imprime_Venta_Granel.objects.create(usuario=request.user,venta_granel=venta)
	return imprime_venta_granel(request)


#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
def imprime_venta_granel(request):
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename=hello.pdf'

	im=Imprime_Venta_Granel.objects.get(usuario=request.user)

	dv=Det_Venta_Granel.objects.filter(venta=im.venta_granel)

	cont_boletas=dv.count()#numero de boletas en la venta

	#cada 28 boletas salta de pagina
	reg_x_pag=28
	#obtenemos el numero de paginas
	num_paginas=math.ceil(cont_boletas/27)

	#obtenemos el abono a imprimir.
	#abono=Imprime_Abono.objects.get(usuario=request.user).abono
	buffer=BytesIO()

	p=canvas.Canvas(buffer,pagesize=A4)

	heigth_row=20#cada renglon es de 20.
	

	# de aqui parriba es el encabezad0
	cont=0

	for x in dv:						
		cont=cont+1
		if fn_modulo(cont,28)==0 or cont==1:				
			current_row=800	
			if cont!=1:			
				p.showPage()
			p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 730,200, 60)

			p.drawString(400,current_row-20,"Pagina 1 de "+str(num_paginas))

			current_row=current_row-heigth_row
			current_row=current_row-heigth_row

			p.setFont("Helvetica",25)

			p.drawString(350,current_row-20,"Venta Granel")

			current_row=current_row-heigth_row-heigth_row

			p.setFont("Helvetica-Bold",10)
			p.drawString(55,current_row,"Folio Venta:")

			p.setFont("Helvetica",10)
			p.drawString(150,current_row,str(im.venta_granel.id))

			current_row=current_row-heigth_row

			p.setFont("Helvetica-Bold",10)
			p.drawString(55,current_row,"Usuario:")


			p.setFont("Helvetica",10)
			p.drawString(150,current_row,im.venta_granel.usuario.username+' - '+im.venta_granel.usuario.first_name+' '+im.venta_granel.usuario.last_name)


			p.setFont("Helvetica-Bold",10)
			p.drawString(350,current_row,"Total Avaluo:")

			p.setFont("Helvetica",10)
			avaluo="{:0,.2f}".format(im.venta_granel.importe_avaluo)
			p.drawString(450,current_row,"$"+avaluo)


			current_row=current_row-heigth_row

			p.setFont("Helvetica-Bold",10)
			p.drawString(55,current_row,"Sucursal:")


			p.setFont("Helvetica",10)
			p.drawString(150,current_row,im.venta_granel.sucursal.sucursal)

			p.setFont("Helvetica-Bold",10)
			p.drawString(350,current_row,"Total Mutuo:")

			mutuo="{:0,.2f}".format(im.venta_granel.importe_mutuo)
			p.setFont("Helvetica",10)
			p.drawString(450,current_row,"$"+mutuo)

			current_row=current_row-heigth_row

			p.setFont("Helvetica-Bold",10)
			p.drawString(55,current_row,"Fecha:")

			p.setFont("Helvetica",10)
			p.drawString(150,current_row,str(im.venta_granel.fecha.strftime("%Y-%m-%d %H:%M:%S")))


			p.setFont("Helvetica-Bold",10)
			p.drawString(350,current_row,"Importe Real Venta:")

			importe_venta="{:0,.2f}".format(im.venta_granel.importe_venta)

			p.setFont("Helvetica",10)
			p.drawString(450,current_row,"$"+importe_venta)

			current_row=current_row-heigth_row
			p.line(55,current_row,530,current_row)

			current_row=current_row-heigth_row	

			p.setFont("Helvetica-Bold",10)
			p.drawString(55,current_row,"Cont")

			p.setFont("Helvetica-Bold",10)
			p.drawString(90,current_row,"F. Boleta")


			p.setFont("Helvetica-Bold",10)
			p.drawString(140,current_row,"Tipo Producto")

			p.setFont("Helvetica-Bold",10)
			p.drawString(250,current_row,"Fec.Venc")

			p.setFont("Helvetica-Bold",10)
			p.drawString(350,current_row,"Mutuo")

			p.setFont("Helvetica-Bold",10)
			p.drawString(450,current_row,"Avaluo")






		current_row=current_row-heigth_row	

		p.setFont("Helvetica",10)
		p.drawString(55,current_row,str(cont))


		p.setFont("Helvetica",10)
		p.drawString(90,current_row,str(x.boleta.folio))

		p.setFont("Helvetica",10)
		p.drawString(140,current_row,x.boleta.tipo_producto.tipo_producto)

		p.setFont("Helvetica",10)
		p.drawString(250,current_row,str(x.boleta.fecha_vencimiento.strftime("%Y-%m-%d")))

		mutuo="{:0,.2f}".format(x.boleta.mutuo)
		p.setFont("Helvetica",10)
		p.drawString(350,current_row,mutuo)
		avaluo="{:0,.2f}".format(x.boleta.avaluo)
		p.setFont("Helvetica",10)
		p.drawString(450,current_row,avaluo)

			


	p.showPage()#terminar pagina actual

	p.save()

	pdf=buffer.getvalue()

	buffer.close()

	response.write(pdf)
	Imprime_Venta_Granel.objects.get(usuario=request.user).delete()
	return response

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

def re_imprimir_abono(request,id_abono):
	abono=Abono.objects.get(id=id_abono)
	Imprime_Abono.objects.filter(usuario=request.user).delete()
	Imprime_Abono.objects.create(usuario=request.user,abono=abono,reimpresion=1)
	return imprime_abono(request)


#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

def imprime_abono(request):	
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename=hello.pdf'

	im=Imprime_Abono.objects.get(usuario=request.user)
	#obtenemos el abono a imprimir.
	abono=Imprime_Abono.objects.get(usuario=request.user).abono
	buffer=BytesIO()

	p=canvas.Canvas(buffer,pagesize=A4)

	heigth_row=20#cada renglon es de 20.
	current_row=800#aqui iniciamos escribir, y por cada renglon, disminuimos heigth_row

	if im.reimpresion==0:
		reimpresion=""
	else:				
		reimpresion="REIMPRESION"
		p.drawImage(settings.IP_LOCAL+'/static/img/img_reimpresion.jpg', 50, -60,500, 500)
		p.drawImage(settings.IP_LOCAL+'/static/img/img_reimpresion.jpg', 50, 350,500, 500)

	p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 750,200, 60)
	p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 370,200, 60)
	cop=0
	while cop<2:
		#p.setFont("Helvetica",20)
		#p.drawString(55,770,"Empeños Express $")

		

		if cop==1:

			p.setFont("Helvetica",7)
			p.drawString(250,current_row,"Copia de Cliente")

		current_row=current_row-heigth_row
		

		p.setFont("Helvetica",10)
		p.drawString(55,current_row-40,"Folio Abono:- "+str(abono.folio))

		p.setFont("Helvetica",25)
		p.drawString(350,current_row,"REFRENDO")

		

		current_row=current_row-heigth_row

		p.setFont("Helvetica",10)
		p.drawString(350,current_row,"Cajero: " + abono.usuario.username)

		current_row=current_row-heigth_row
		

	

		p.setFont("Helvetica-Bold",10)
		p.drawString(350,current_row,str(abono.fecha.strftime("%Y-%m-%d %H:%M:%S")))

		current_row=current_row-heigth_row

		p.setFont("Helvetica-Bold",10)
		p.drawString(55,current_row,"Cliente:- ")
		p.setFont("Helvetica",10)
		p.drawString(130,current_row,str(abono.boleta.cliente))



		importe_a_refrendo=math.ceil(fn_importe_a_refrendo(abono))

		p.setFont("Helvetica",10)
		p.drawString(350,current_row,"Abono a Refrendo:- ")

		importe_a_refrendo="{:0,.2f}".format(importe_a_refrendo)

		p.drawString(480,current_row,"$"+str(importe_a_refrendo)+"")

		current_row=current_row-heigth_row

		p.setFont("Helvetica-Bold",10)
		p.drawString(55,current_row,"Folio Boleta:- ")
		p.setFont("Helvetica",10)
		p.drawString(130,current_row,str(abono.boleta.folio))

		
		importe_a_pg=round(fn_importe_a_pg(abono),2)

		p.setFont("Helvetica",10)
		p.drawString(350,current_row,"Abono a PG:- ")

		importe_a_pg="{:0,.2f}".format(importe_a_pg)


		p.drawString(480,current_row,"$"+str(importe_a_pg)+"")


		#nueva linea
		current_row=current_row-heigth_row

		p.setFont("Helvetica-Bold",10)
		p.drawString(55,current_row,"Sucursal:- ")
		p.setFont("Helvetica",10)
		p.drawString(130,current_row,abono.boleta.sucursal.sucursal)


		importe_a_cap=round(fn_importe_a_cap(abono),2)
		p.setFont("Helvetica",10)
		p.drawString(350,current_row,"Abono a Capital:- ")
		importe_a_cap="{:0,.2f}".format(importe_a_cap)

		p.drawString(480,current_row,"$"+str(importe_a_cap))

		#nueva linea
		current_row=current_row-heigth_row


		
		p.setFont("Helvetica",7)
		p.drawString(130,current_row,abono.boleta.caja.sucursal.calle+' No. Int. '+str(abono.boleta.caja.sucursal.numero_interior)+' No. ext. '+str(abono.boleta.caja.sucursal.numero_exterior)+' CP '+str(abono.boleta.caja.sucursal.codigo_postal))



		importe_desemp=round(fn_importe_desemp(abono),2)
		p.setFont("Helvetica",10)
		p.drawString(350,current_row,"Desempeño:- ")

		importe_desemp="{:0,.2f}".format(importe_desemp)

		p.drawString(480,current_row,"$"+str(importe_desemp)+"")
		p.line(350,current_row-2,530,current_row-2)

		#nueva linea
		current_row=current_row-heigth_row	
		p.setFont("Helvetica",7)
		p.drawString(130,current_row,abono.boleta.caja.sucursal.colonia+', '+abono.boleta.caja.sucursal.ciudad+' '+abono.boleta.caja.sucursal.estado+', '+abono.boleta.caja.sucursal.pais)



		p.setFont("Helvetica-Bold",10)
		p.drawString(350,current_row,"Total Abono:- ")
		importe="{:0,.2f}".format(abono.importe)

		p.drawString(480,current_row,"$"+str(importe))

		#nueva linea
		current_row=current_row-heigth_row	
		current_row=current_row-heigth_row	
		

		p.setFont("Helvetica-Bold",10)
		p.drawString(55,current_row,"Fecha ven.:- ")
		p.setFont("Helvetica",10)
		p.drawString(130,current_row,str(abono.boleta.fecha_vencimiento))

		p.setFont("Helvetica",10)

		p.drawString(350,current_row,"Nuevo Mutuo:- ")
		mutuo="{:0,.2f}".format(abono.boleta.mutuo)

		p.drawString(480,current_row,"$"+str(mutuo))

		current_row=current_row-heigth_row	


		articulo=""
		if abono.boleta.tipo_producto.id==3:
			articulo=Det_Boleto_Empeno.objects.get(boleta_empeno=abono.boleta).descripcion
		else:
			articulo=abono.boleta.tipo_producto.tipo_producto

		p.setFont("Helvetica-Bold",10)
		p.drawString(55,current_row,"Artículo:- ")
		p.setFont("Helvetica",10)
		p.drawString(130,current_row,articulo)

		

		#plazo semanal
		if abono.boleta.plazo.id==2:
			#todos los abonos que no han sido pagados y que ya estan vencidos.
			
			pag_vencido=Pagos.objects.filter(boleta=abono.boleta,pagado='N',vencido="S").aggregate(Sum("importe"))

			if pag_vencido["importe__sum"]==None:
				importe_saldo_vencido=0.00
			else:
				importe_saldo_vencido=pag_vencido["importe__sum"]

		#plazo mensual
		if abono.boleta.plazo.id==3:
			pag_vencido=Periodo.objects.filter(boleta=abono.boleta,pagado="N",vencido="S").aggregate(Sum("importe"))
			if pag_vencido["importe__sum"]==None:
				importe_saldo_vencido=0.00
			else:
				importe_saldo_vencido=pag_vencido["importe__sum"]


		p.setFont("Helvetica-Bold",10)

		importe_saldo_vencido="{:0,.2f}".format(math.ceil(importe_saldo_vencido))
		
		p.drawString(350,current_row,"Saldo Vencido:- ")
		p.drawString(480,current_row,"$"+str(importe_saldo_vencido))




		current_row=current_row-heigth_row	

		p.setFont("Helvetica-Bold",10)
		p.drawString(55,current_row,"Fechas Pago")

		current_row=current_row-heigth_row	

		p.line(55,current_row,550,current_row)	
		p.line(55,current_row,55,current_row-80)	
		p.line(55,current_row-80,550,current_row-80)			
		p.line(550,current_row,550,current_row-80)	

		

		#encabezado
		p.setFont("Helvetica-Bold",10)
		p.drawString(60,current_row+2,"No.Pago")
		
		p.drawString(131,current_row+2,"Fecha")
		p.drawString(202,current_row+2,"Almacenaje")
		p.drawString(273,current_row+2,"Interes")		
		p.drawString(344,current_row+2,"Impuesto")
		p.drawString(415,current_row+2,"Refrendo")
		p.drawString(486,current_row+2,"Desempeño")


		current_row=current_row-heigth_row	

		p.line(55,current_row,550,current_row)	
		current_row=current_row-heigth_row	

		p.line(55,current_row,550,current_row)	
		current_row=current_row-heigth_row	

		p.line(55,current_row,550,current_row)		
		current_row=current_row-heigth_row	
		p.line(55,current_row,550,current_row)





		est_comisionpg=Tipo_Pago.objects.get(id=2)

		#plazo semanal
		if abono.boleta.plazo.id==2:
			pa=Pagos.objects.filter(boleta=abono.boleta,pagado = 'N').exclude(tipo_pago = est_comisionpg).order_by("id")

			cont=0
			if cop==0:
				linea=522
			else:
				linea=142

			for x in pa:		
				cont=cont+1
				p.setFont("Helvetica",7)
				p.drawString(60,linea,str(cont))
				p.drawString(131,linea,str(x.fecha_vencimiento.strftime('%d/%m/%Y')))
				almacenaje=x.almacenaje*decimal.Decimal(cont)
				p.drawString(202,linea,"$"+str(almacenaje))
				interes=x.interes*decimal.Decimal(cont)
				p.drawString(273,linea,"$"+str(interes))
				iva=x.iva*decimal.Decimal(cont)
				p.drawString(344,linea,"$"+str(iva))
				#refrendo=iva+interes+almacenaje
				p.drawString(415,linea,"$"+str(x.importe*cont))
				imp_desempeno = "{:0,.2f}".format(math.ceil((x.importe*cont)+x.boleta.mutuo))
				p.drawString(486,linea,"$" + imp_desempeno)
				linea=linea-20

		#plazo mensual
		if abono.boleta.plazo.id == 3:

			pa=Periodo.objects.filter(boleta=abono.boleta,pagado="N",vencido="N")

			cont=0
			if cop==0:
				linea=522
			else:
				linea=142

			resp = abono.boleta.fn_calcula_refrendo()

			#si existen pagos parciales no vencidos sin pagar, los mostramos como fechas proximo pago,
			#en caso de no existir solo mostramos un proximo pago como si fuera mensual
			if pa.exists():

				for x in pa:		
					cont=cont+1
					p.setFont("Helvetica",7)
					p.drawString(60,linea,str(cont))
					p.drawString(131,linea,str(x.fecha_vencimiento.strftime('%d/%m/%Y')))
					almacenaje = "{:0,.2f}".format((resp[0]["almacenaje"]/4)*cont)
					p.drawString(202,linea,"$"+str(almacenaje))
					interes = "{:0,.2f}".format((resp[0]["interes"]/4)*cont)
					p.drawString(273,linea,"$"+str(interes))
					iva = "{:0,.2f}".format((resp[0]["iva"]/4)*cont)
					p.drawString(344,linea,"$"+str(iva))
					refrendo = "{:0,.2f}".format((resp[0]["refrendo"]/4)*cont)
					p.drawString(415,linea,"$"+refrendo)
					p.drawString(486,linea,"$"+str(math.ceil((x.importe*cont)+x.boleta.mutuo)))
					linea=linea-20

			else:
				
				cont=cont+1
				p.setFont("Helvetica",7)
				p.drawString(60,linea,str(cont))
				p.drawString(131,linea,str(abono.boleta.fecha_vencimiento.strftime('%d/%m/%Y')))
				almacenaje = "{:0,.2f}".format(resp[0]["almacenaje"])
				p.drawString(202,linea,"$"+str(almacenaje))
				interes = "{:0,.2f}".format(resp[0]["interes"])
				p.drawString(273,linea,"$"+str(interes))
				iva = "{:0,.2f}".format(resp[0]["iva"])
				p.drawString(344,linea,"$"+str(iva))
				refrendo = "{:0,.2f}".format(resp[0]["refrendo"])
				p.drawString(415,linea,"$"+refrendo)

				p.drawString(486,linea,"$"+str(math.ceil((abono.boleta.refrendo)+abono.boleta.mutuo)))
				linea=linea-20

		current_row=current_row-heigth_row	

		u=0
		pinta=0
		while u<600:
			if pinta==0:
				p.line(u,current_row,u+10,current_row)#pintamos linea de corte
				pinta=1
			else:
				pinta=0

			u=u+10
		current_row=current_row-heigth_row	
		
		cop=cop+1

	try:
		rac=Rel_Abono_Capital.objects.get(abono=abono)		
		capital_restante=rac.capital_restante
	except:
		print("no abono a capital")
		capital_restante=-1


	
	#si el el abono dejo el capital de la boleta en cero, imprimimos recibo de desempeño
	if int(capital_restante)==int(0):
		p.showPage()#terminar pagina actual
		heigth_row=20#cada renglon es de 20.
		current_row=800#aqui iniciamos escribir, y por cada renglon, disminuimos heigth_row

		if im.reimpresion==0:
			reimpresion=""
		else:				
			reimpresion="REIMPRESION"
			p.drawImage(settings.IP_LOCAL+'/static/img/img_reimpresion.jpg', 50, -80,500, 500)
			p.drawImage(settings.IP_LOCAL+'/static/img/img_reimpresion.jpg', 50, 350,500, 500)

		p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 730,200, 60)
		p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 340,200, 60)

		cop=0
		while cop<2:

			if cop==1:
				
				p.setFont("Helvetica",15)
				p.drawString(250,current_row,"Copia de Cliente")
			current_row=current_row-heigth_row
			current_row=current_row-heigth_row

			p.setFont("Helvetica",10)
			p.drawString(55,current_row-40,"Folio Abono:- "+str(abono.folio))

			p.setFont("Helvetica",25)
			p.drawString(350,current_row,"DESEMPEÑO")

			

			current_row=current_row-heigth_row			
			current_row=current_row-heigth_row
			



			p.setFont("Helvetica-Bold",10)
			p.drawString(350,current_row,str(abono.fecha))

			current_row=current_row-heigth_row

			p.setFont("Helvetica-Bold",10)
			p.drawString(55,current_row,"Cliente:- ")
			p.setFont("Helvetica",10)
			p.drawString(130,current_row,str(abono.boleta.cliente))



			importe_a_refrendo=round(fn_importe_a_refrendo(abono),2)

			p.setFont("Helvetica",10)
			p.drawString(350,current_row,"Abono a Refrendo:- ")
			p.drawString(480,current_row,"$"+str(importe_a_refrendo)+"")

			current_row=current_row-heigth_row

			p.setFont("Helvetica-Bold",10)
			p.drawString(55,current_row,"Folio Boleta:- ")
			p.setFont("Helvetica",10)
			p.drawString(130,current_row,str(abono.boleta.folio))

			
			importe_a_pg=round(fn_importe_a_pg(abono),2)

			p.setFont("Helvetica",10)
			p.drawString(350,current_row,"Abono a PG:- ")

			p.drawString(480,current_row,"$"+str(importe_a_pg)+"")


			#nueva linea
			current_row=current_row-heigth_row

			p.setFont("Helvetica-Bold",10)
			p.drawString(55,current_row,"Sucursal:- ")
			p.setFont("Helvetica",10)
			p.drawString(130,current_row,abono.boleta.sucursal.sucursal)


			importe_a_cap=round(fn_importe_a_cap(abono),2)
			p.setFont("Helvetica",10)
			p.drawString(350,current_row,"Abono a Capital:- ")
			p.drawString(480,current_row,"$"+str(importe_a_cap)+"")

			#nueva linea
			current_row=current_row-heigth_row


			
			p.setFont("Helvetica",7)
			p.drawString(130,current_row,abono.boleta.caja.sucursal.calle+' No. Int. '+str(abono.boleta.caja.sucursal.numero_interior)+' No. ext. '+str(abono.boleta.caja.sucursal.numero_exterior)+' CP '+str(abono.boleta.caja.sucursal.codigo_postal))



			importe_desemp=round(fn_importe_desemp(abono),2)
			p.setFont("Helvetica",10)
			p.drawString(350,current_row,"Desempeño:- ")
			p.drawString(480,current_row,"$"+str(importe_desemp)+"")
			p.line(350,current_row-2,530,current_row-2)

			#nueva linea
			current_row=current_row-heigth_row	
			p.setFont("Helvetica",7)
			p.drawString(130,current_row,abono.boleta.caja.sucursal.colonia+', '+abono.boleta.caja.sucursal.ciudad+' '+abono.boleta.caja.sucursal.estado+', '+abono.boleta.caja.sucursal.pais)



			p.setFont("Helvetica-Bold",10)
			p.drawString(350,current_row,"Total Abono:- ")
			p.drawString(480,current_row,"$"+str(abono.importe))
			current_row=current_row-heigth_row	


			articulo=""

			if abono.boleta.tipo_producto.id==3:
				articulo=Det_Boleto_Empeno.objects.get(boleta_empeno=abono.boleta).descripcion
			else:
				articulo=abono.boleta.tipo_producto.tipo_producto

			p.setFont("Helvetica-Bold",10)
			p.drawString(55,current_row,"Artículo:- ")
			p.setFont("Helvetica",10)
			p.drawString(130,current_row,articulo)

			current_row=current_row-heigth_row	
			current_row=current_row-heigth_row	
			current_row=current_row-heigth_row	
			current_row=current_row-heigth_row	

			p.line(100,current_row,250,current_row)
			p.line(350,current_row,500,current_row)
			current_row=current_row-heigth_row	
			p.drawString(150,current_row,"Cliente")
			p.drawString(400,current_row,"Proveedor")


			current_row=current_row-heigth_row	
			current_row=current_row-heigth_row	
			u=0
			pinta=0
			while u<600:
				if pinta==0:
					p.line(u,current_row,u+10,current_row)#pintamos linea de corte
					pinta=1
				else:
					pinta=0

				u=u+10

			cop=cop+1
			current_row=current_row-heigth_row	
			current_row=current_row-heigth_row	

	p.showPage()#terminar pagina actual

	p.save()

	pdf=buffer.getvalue()

	buffer.close()

	response.write(pdf)
	Imprime_Abono.objects.get(usuario=request.user).delete()
	return response

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

def re_imprimir_boleta(request,id_boleta):
	boleta=Boleta_Empeno.objects.get(id=id_boleta)
	Imprimir_Boletas.objects.filter(usuario=request.user).delete()
	Imprimir_Boletas.objects.create(usuario=request.user,boleta=boleta,reimpresion=1)
	return imprime_boleta(request)

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

def imprime_boleta(request):
	#buscamos las boletas que se van a imprimir
	boletas=Imprimir_Boletas.objects.filter(usuario=request.user)

	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename=hello.pdf'


	buffer=BytesIO()

	p=canvas.Canvas(buffer,pagesize=A4)

	for x in boletas:



		#obtenemos el numero de ojas que saldran de esta boleta.
		ndet=Det_Boleto_Empeno.objects.filter(boleta_empeno=x.boleta).count()
		rinicial=0
		size=9
		no_paginas=math.ceil(ndet/size)
		cont_pag=1
		while cont_pag<=no_paginas:
			#p.setFont("Helvetica",20)
			#p.drawString(55,770,"Empeños Express $")
			if x.reimpresion==0:
				reimpresion=""
			else:				
				reimpresion="REIMPRESION"
				p.drawImage(settings.IP_LOCAL+'/static/img/img_reimpresion.jpg', 50, 300,500, 500)

			p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 750,200, 60)

			#cuadro 1] Informaciond de la empresa
			p.line(50,750,50,665)	
			p.line(50,750,280,750)
			p.line(280,750,280,665)	
			p.line(50,665,280,665)

			p.setFont("Helvetica-Bold",7)
			p.drawString(55,740,"Empresa:")
			p.setFont("Helvetica",7)
			p.drawString(55,730,"   " + Empresa.objects.get(id = 1).nombre_empresa)
			p.setFont("Helvetica",7)
			p.drawString(55,720,"      "+Empresa.objects.get(id = 1).horario)

			p.setFont("Helvetica-Bold",7)
			p.drawString(55,700,"RFC:")
			p.setFont("Helvetica",7)
			p.drawString(75,700,Empresa.objects.get(id = 1).rfc)
			p.setFont("Helvetica-Bold",7)
			p.drawString(170,700,"Telefono:")
			p.setFont("Helvetica",7)
			p.drawString(210,700,x.boleta.caja.sucursal.telefono)


			p.setFont("Helvetica-Bold",7)
			p.drawString(55,690,"Dirección:")
			p.setFont("Helvetica",7)
			p.drawString(100,690,x.boleta.caja.sucursal.calle+' No. Int. '+str(x.boleta.caja.sucursal.numero_interior)+' No. ext. '+str(x.boleta.caja.sucursal.numero_exterior))
			p.setFont("Helvetica",7)
			p.drawString(55,680,' CP '+str(x.boleta.caja.sucursal.codigo_postal)+' '+x.boleta.caja.sucursal.colonia+', '+x.boleta.caja.sucursal.ciudad+' '+x.boleta.caja.sucursal.estado+', '+x.boleta.caja.sucursal.pais)



			#cuadro 2] Informacion general de la boleta
			p.line(300,780,300,665)	
			p.line(300,780,550,780)
			p.line(550,780,550,665)	
			p.line(300,665,550,665)

			p.setFont("Helvetica-Bold",10)


			p.drawString(305,770,"BOLETA DE EMPEÑO")

			p.drawString(455,790,"Pag: "+str(cont_pag)+' de '+str(no_paginas))

			p.setFont("Helvetica-Bold",15)
			p.drawString(305,750,"No. Boleta:")
			p.setFont("Helvetica-Bold",15)
			p.drawString(455,750, str(IDENTIFICADOR_TIENDA) + "-" + fn_str_clave(x.boleta.folio))



			p.setFont("Helvetica-Bold",10)
			p.drawString(305,730,"Avaluo:")
			p.setFont("Helvetica",10)
			type(x.boleta.refrendo)
			type(x.boleta.avaluo)

			avaluo=format(x.boleta.avaluo,',d')
			p.drawString(365,730,"$"+avaluo+".00")

			p.setFont("Helvetica-Bold",10)
			p.drawString(305,715,"Refrendo:")

			p.setFont("Helvetica",10)
			refrendo=format(int(x.boleta.refrendo),',d')
			p.drawString(365,715,"$"+str(refrendo)+".00")

			p.setFont("Helvetica-Bold",10)
			p.drawString(305,700,"Mutuo:")
			p.setFont("Helvetica",10)
			mutuo=format(int(x.boleta.mutuo),',d')
			p.drawString(365,700,"$"+mutuo+".00")



			p.setFont("Helvetica-Bold",10)
			p.drawString(305,685,"Fecha Emi.:")
			p.setFont("Helvetica",10)
			p.drawString(365,685,str(x.boleta.fecha.strftime("%Y-%m-%d %H:%M:%S")))


			p.setFont("Helvetica-Bold",10)
			p.drawString(305,670,"Fecha Ven.:")
			p.setFont("Helvetica",10)
			
			fecha_vencimiento = datetime.combine(x.boleta.fecha_vencimiento, time.min) 
			p.drawString(365,670,str(fecha_vencimiento.strftime("%Y-%m-%d %H:%M:%S")))


			#cuadro 3] Informacion de Cliente
			p.line(50,660,50,595)	
			p.line(550,660,550,595)	
			p.line(50,660,550,660)	
			p.line(50,595,550,595)	

			p.setFont("Helvetica-Bold",7)
			p.drawString(55,645,"CLIENTE:")
			p.setFont("Helvetica",7)
			p.drawString(105,645,x.boleta.cliente.nombre+' '+x.boleta.cliente.apellido_p+' '+x.boleta.cliente.apellido_m)

			p.setFont("Helvetica-Bold",7)
			p.drawString(305,645,"COTITULAR:")
			p.setFont("Helvetica",7)
			p.drawString(350,645,x.boleta.nombre_cotitular+' '+x.boleta.apellido_p_cotitular+' '+x.boleta.apellido_m_cotitular)

			p.setFont("Helvetica-Bold",7)
			p.drawString(55,630,"Dirección:")
			p.setFont("Helvetica",7)
			p.drawString(105,630,x.boleta.cliente.calle+' No. Int.: '+str(x.boleta.cliente.numero_interior)+' No. Ext.: '+str(x.boleta.cliente.numero_exterior)+', '+str(x.boleta.cliente.codigo_postal)+', '+x.boleta.cliente.colonia+', '+x.boleta.cliente.ciudad+', '+x.boleta.cliente.estado+', '+x.boleta.cliente.pais)

			p.setFont("Helvetica-Bold",7)
			p.drawString(55,615,"Telefono Fijo: ")


			p.setFont("Helvetica",7)
			p.drawString(120,615,x.boleta.cliente.telefono_fijo)

			p.setFont("Helvetica-Bold",7)
			p.drawString(55,600,"Telefono Celular: ")

			p.setFont("Helvetica",7)
			p.drawString(120,600,x.boleta.cliente.telefono_celular)


			#cuadro 4] Datos de Empeño
			p.line(50,590,50,525)	
			p.line(550,590,550,525)		
			p.line(50,590,550,590)			
			p.line(50,525,550,525)


			p.setFont("Helvetica-Bold",7)
			p.drawString(55,575,"DATOS DEL EMPEÑO:")

			p.setFont("Helvetica-Bold",7)
			p.drawString(55,560,"Descripción: ")


			p.setFont("Helvetica",7)
			p.drawString(130,560,x.boleta.tipo_producto.tipo_producto)

			p.setFont("Helvetica-Bold",7)
			p.drawString(315,560,"Refrendo: ")

			p.setFont("Helvetica",7)
			p.drawString(400,560,"$"+str(x.boleta.refrendo))



			p.setFont("Helvetica-Bold",7)
			p.drawString(55,545,"Sucursal: ")


			p.setFont("Helvetica",7)
			p.drawString(130,545,x.boleta.caja.sucursal.sucursal)

			p.setFont("Helvetica-Bold",7)
			p.drawString(315,545,"Plazo: ")

			p.setFont("Helvetica",7)
			p.drawString(400,545,x.boleta.plazo.plazo)


			p.setFont("Helvetica-Bold",7)
			p.drawString(315,530,"Fecha Limite: ")

			fecha_vencimiento = datetime.combine(x.boleta.fecha_vencimiento, time.min)	 

			p.setFont("Helvetica",7)
			p.drawString(400,530,str(fecha_vencimiento))



			p.setFont("Helvetica-Bold",7)
			p.drawString(55,505,"Articulos")

			#cuadro de articulos
			p.line(55,500,550,500)			
			p.line(55,500,55,350)
			p.line(55,350,550,350)					
			p.line(550,350,550,500)

			#lineas cuadro articulos
			p.line(55,485,550,485)	
			p.line(55,470,550,470)	
			p.line(55,455,550,455)	
			p.line(55,440,550,440)	
			p.line(55,425,550,425)		

			p.line(55,410,550,410)		
			p.line(55,395,550,395)		
			p.line(55,380,550,380)		
			p.line(55,365,550,365)		
			p.line(55,350,550,350)

				

			#columna articulos
			p.line(90,500,90,350)
			p.line(300,500,300,350)
			p.line(350,500,350,350)
			p.line(400,500,400,350)
			p.line(450,500,450,350)
			p.line(500,500,500,350)

			#encabezado
			p.setFont("Helvetica-Bold",7)
			p.drawString(60,487,"No.")		
			p.drawString(95,487,"Descripción.")
			p.drawString(305,487,"Metal.")
			p.drawString(355,487,"Peso (gr).")
			p.drawString(405,487,"Avaluo.")
			p.drawString(455,487,"Impuesto.")
			p.drawString(505,487,"Mutuo.")

		
			inicio=0
			if rinicial==0:
				inicio=0
			else:
				inicio=rinicial-1

			db=Det_Boleto_Empeno.objects.filter(boleta_empeno=x.boleta)[inicio:rinicial+size]

			linea=487
			impuesto_total=0.00


			cont=0
			str_linea=""

			descripcion_talon=""
			descripcion_talon_obser=""
			for y in db:
				cont=cont+1
				str_linea=y.linea.linea
				linea=linea-15
				#calculamos el impuesto
				#si es oro o plata
				impuesto=0.00
				 
				"""if x.boleta.tipo_producto.id==1 or x.boleta.tipo_producto.id==2: 				
					almacenaje=(y.mutuo*0.05)
					interes=(y.mutuo*0.063)
					impuesto=((almacenaje+interes)*0.16)			

				else:
					almacenaje=(y.mutuo*0.072)
					interes=(y.mutuo*0.1263)
					impuesto=((almacenaje+interes)*0.16)
				"""
				impuesto = x.boleta.fn_calcula_refrendo()[0]["refrendo"]

				impuesto_total=impuesto_total+impuesto
				

				p.setFont("Helvetica",7)
				p.drawString(60,linea,str(cont))	

				descripcion_talon=y.descripcion
				
				p.drawString(95,linea,y.descripcion)
				if y.tipo_producto.id==1 or  y.tipo_producto.id==2:
					p.drawString(305,linea,y.costo_kilataje.kilataje)
					p.drawString(355,linea,str(y.peso))
				avaluo=format(y.avaluo,',d')
				p.drawString(405,linea,"$"+avaluo+".00")
				impuesto=format(int(round(impuesto,2)),',d')
				p.drawString(455,linea,"$"+str(impuesto)+'.00')
				mutuo=format(y.mutuo,',d')
				p.drawString(505,linea,"$"+mutuo+".00")

			if x.boleta.tipo_producto.id==3:				
				linea=linea-15				
				descripcion_talon_obser=y.observaciones
				p.drawString(95,linea,"Obser: "+str(y.observaciones))
			else:
				descripcion_talon_obser=y.tipo_producto.tipo_producto

			p.setFont("Helvetica-Bold",7)
			p.drawString(55,530,"Linea")		
			p.setFont("Helvetica",7)
			p.drawString(130,530,str_linea)
			
			#cuadro 7] Tabla de pagos
			p.setFont("Helvetica-Bold",7)
			p.drawString(55,330,"Pagos:")

			p.line(55,250,550,250)	
			p.line(55,250,55,325)	
			p.line(55,325,550,325)			
			p.line(550,250,550,325)	

			
			#lineas de tabla de pagos	
			p.line(55,310,550,310)	
			p.line(55,295,550,295)	
			p.line(55,280,550,280)	
			p.line(55,265,550,265)		
			p.line(55,250,550,250)

			#colimnas de tabla de pago
			p.line(126,250,126,325)	#numero de pago
			p.line(197,250,197,325)	#fecha pago
			p.line(268,250,268,325)	#Almacenaje
			p.line(339,250,339,325)	#Interes
			p.line(410,250,410,325)	#IVA
			p.line(481,250,481,325)	#Refrendo
			#p.line(455,110,455,185)	#Desempeño

			#encabezado
			p.setFont("Helvetica-Bold",7)
			p.drawString(60,312,"No.Pago")
			
			p.drawString(131,312,"Fecha")
			p.drawString(202,312,"Almacenaje")
			p.drawString(273,312,"Interes")		
			p.drawString(344,312,"Impuesto")
			p.drawString(415,312,"Refrendo")
			p.drawString(486,312,"Desempeño")

			#tipo de pago refrendo
			refrendo=Tipo_Pago.objects.get(id=1)
			pa=Pagos.objects.filter(boleta=x.boleta,pagado='N',tipo_pago=refrendo).order_by("id")

			cont=0
			linea=297
			for x in pa:
				cont=cont+1
				p.setFont("Helvetica",7)
				p.drawString(60,linea,str(cont))
				p.drawString(131,linea,str(x.fecha_vencimiento.strftime('%d/%m/%Y')))

				almacenaje=x.almacenaje*decimal.Decimal(cont)
				almacenaje="{:0,.2f}".format(almacenaje)

				p.drawString(202,linea,"$"+str(almacenaje))
				interes=x.interes*decimal.Decimal(cont)
				interes="{:0,.2f}".format(interes)

				p.drawString(273,linea,"$"+str(interes))
				iva=x.iva*decimal.Decimal(cont)

				iva="{:0,.2f}".format(iva)

				p.drawString(344,linea,"$"+str(iva))
				#refrendo=iva+interes+almacenaje


				refrendo="{:0,.2f}".format(x.importe*cont)

				p.drawString(415,linea,"$"+str(refrendo))

				desempeno="{:0,.2f}".format(math.ceil((x.importe*cont)+x.boleta.mutuo))

				p.drawString(486,linea,"$"+str(desempeno))
				linea=linea-15

			#cuadro 6] Firma Cliente
			p.line(55,215,250,215)	
			p.line(55,185,250,185)	
			p.line(55,215,55,185)
			p.line(250,215,250,185)

			p.setFont("Helvetica-Bold",10)
			p.drawString(135,190,"Cliente")

			#cuadro 7] Firma Valuador
			p.line(355,215,550,215)	
			p.line(355,185,550,185)	
			p.line(355,215,355,185)
			p.line(550,215,550,185)

			p.setFont("Helvetica-Bold",10)
			p.drawString(390,190,"Valuador: "+ x.boleta.usuario.username)

			p.setFont("Helvetica-Bold",7)
			obj_interes = Configuracion_Interes_Empeno.objects.get(sucursal = x.boleta.sucursal)
			imp_interes = ""
			imp_almacenaje = ""

			#La comision del pg es por empresay no importa que tipo de producto sea
			desemp_ext = "{:0,.2f}".format(Porcentaje_Comision_PG.objects.get(id = 1).porcentaje)

			porcentaje = Porcentaje_Sobre_Avaluo.objects.all().aggregate(Sum("porcentaje"))
			porce = 0;
			if porcentaje["porcentaje__sum"]!=None:
				porce = decimal.Decimal(porcentaje["porcentaje__sum"])
			comercializacion = "{:0,.2f}".format(porce)

			if x.boleta.tipo_producto.id == 1:#oro
				imp_interes = "{:0,.2f}".format(obj_interes.interes_oro)
				imp_almacenaje = "{:0,.2f}".format(obj_interes.almacenaje_oro)

			elif x.boleta.tipo_producto.id ==2:#plata
				imp_interes = "{:0,.2f}".format(obj_interes.interes_plata)
				imp_almacenaje = "{:0,.2f}".format(obj_interes.almacenaje_plata)
			elif x.boleta.tipo_producto.id ==3:#varios
				imp_interes = "{:0,.2f}".format(obj_interes.interes_prod_varios)
				imp_almacenaje = "{:0,.2f}".format(obj_interes.almacenaje_prod_varios)
			
			p.drawString(55,235,"Intereses: " +  str(imp_interes) + "%")
			p.drawString(150,235,"Almacenaje: " +  str(imp_almacenaje) + "%")
			p.drawString(250,235,"Desempeño extemporaneo: " +  str(desemp_ext) + "%")			
			p.drawString(400,235,"Comercialización: " +  str(comercializacion) + "%")
			fecha_com = datetime.combine(x.boleta.fecha_vencimiento + timedelta(days = 1),time.min )
			fecha_com = datetime.strftime(fecha_com,'%Y-%m-%d')
			p.drawString(55,225,"Fecha de comercialización de la(s) prenda(s): " +  str(fecha_com) )
			p.drawString(250,225,"Costo Anual Total (CAT): " +  "115.96%" )

			u=0
			pinta=0
			while u<600:
				if pinta==0:
					p.line(u,180,u+10,180)#pintamos linea de corte
					pinta=1
				else:
					pinta=0

				u=u+10

			p.line(55,100,180,100)
			p.drawString(100,80,"Cliente")

			p.line(420,100,545,100)

			p.drawString(420,80,"Valuador: "+ x.boleta.usuario.username)


			p.line(200,160,400,160)
			p.line(200,55,200,160)
			p.line(200,55,400,55)		
			p.line(400,55,400,160)

			p.setFont("Helvetica-Bold",15)
			p.drawString(205,140,"No. Boleta: "+str(x.boleta.folio))

			p.setFont("Helvetica-Bold",7)
			avaluo="{:0,.2f}".format(x.boleta.avaluo)
			mutuo="{:0,.2f}".format(x.boleta.mutuo)

			p.drawString(205,130,"Avaluo: "+"$"+str(avaluo)+"     Mutuo: $"+mutuo)
			p.setFont("Helvetica",7)
			

			#p.drawString(255,130,"$"+str(avaluo))


			p.setFont("Helvetica",7)
			p.drawString(205,115,descripcion_talon)
			p.drawString(205,100,descripcion_talon_obser)



			p.setFont("Helvetica-Bold",7)
			p.drawString(205,85,"Fecha Emi.:")
			p.setFont("Helvetica",7)
			p.drawString(255,85,str(x.boleta.fecha.strftime("%Y-%m-%d %H:%M:%S")))


			p.setFont("Helvetica-Bold",7)
			p.drawString(205,70,"Fecha Ven.:")
			p.setFont("Helvetica",7)
			
			fecha_vencimiento = datetime.combine(x.boleta.fecha_vencimiento, time.min) 
			p.drawString(255,70,str(fecha_vencimiento))


			rinicial=rinicial+10
			cont_pag=cont_pag+1			
			p.showPage()#terminar pagina actual

	p.save()

	pdf=buffer.getvalue()

	buffer.close()

	response.write(pdf)
	Imprimir_Boletas.objects.filter(usuario=request.user).delete()
	return response



#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
@api_view(['GET'])
def api_envia_token(request):
	

	#el token se genero al entrar a la pantalla d retiro de efectivo, aqui solamente lo enviamos.c
	asunto	= request.GET.get("asunto")
	usuario = request.GET.get("usuario")
	sucursal = request.GET.get("sucursal")
	caja = request.GET.get("caja")
	importe = request.GET.get("importe")
	comentarios = request.GET.get("comentarios")
	token = request.GET.get("token")
	id_concepto = request.GET.get("id_concepto")

	
	obj_token = Token.objects.get(token = int(token))
	obj_token.aux_1 = id_concepto
	obj_token.save()

	concepto = Concepto_Retiro.objects.get(id = int(id_concepto))
	
	respuesta=[]
	if request.method=="GET":
		html="<html><head></head><body>"
		html=html+"El usuario "+ usuario+ " de la sucursal <strong>"+sucursal+ "</strong> en la <strong> caja "+caja +" </strong>, solicita tu autorizacion para realizar un retiro de efectivo. <br><br>Importe: <strong> $"+str(importe)+ ".00</strong> <br><br>Concepto: <strong>"+concepto.concepto+"</strong><br><br>Comentario: <strong> "+comentarios+"</strong>.<br><br><br>Folio de Autorizacion: "+token
		html=html+"</body></html>"


		html = html.replace("\xa1", "")
		html = html.replace("\xbf", "")
		html = html.replace("\xd1", "N")
		html = html.replace("\xdc", "U")
		html = html.replace("\xf1", "n")
		html = html.replace("\x0a", "\n")

		html = html.replace("\xe1", "a")		
		html = html.replace("\xe9", "e")		
		html = html.replace("\xed", "i")		
		html = html.replace("\xf3", "o")				
		html = html.replace("\xfa", "u")


		html = html.replace("\xc1", "A")		
		html = html.replace("\xc9", "E")		
		html = html.replace("\xcd", "I")		
		html = html.replace("\xd3", "O")				
		html = html.replace("\xda", "U")
		server = smtplib.SMTP('smtp.gmail.com:587')
		msg = email.message.Message()
		msg['Subject'] = asunto	

		msg['From']=settings.EMAIL_HOST_USER
		msg['To']=settings.EMAIL_NOTIFICACIONES
		password = settings.EMAIL_HOST_PASSWORD
		print(password)
		msg.add_header('Content-Type', 'text/html')
		msg.set_payload(html)		
		s = smtplib.SMTP('smtp.gmail.com:587')
		s.starttls()		
		# Login Credentials for sending the mail
		s.login(msg['From'], password)		
		s.sendmail(msg['From'], [msg['To']], msg.as_string())
	return Response(respuesta)
#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
def fn_envia_mail_diferencia_cierre_caja(caja):
	if int(caja.diferencia)!=0:
		html="<html><head></head><body>"
		html=html+"La caja <strong>"+caja.caja+"</strong>, del usuario <strong>"+caja.usuario.first_name+" "+caja.usuario.last_name+"</strong>, en la sucursal <strong>"+caja.sucursal.sucursal+"</strong>, cerro con una diferencia de: $"+str(caja.diferencia)+"."
		html=html+"<br><br><br>"
		html=html+"<strong>Comentarios:</strong>: "+caja.comentario		
		html=html+"</body></html>"


		html = html.replace("\xa1", "")
		html = html.replace("\xbf", "")
		html = html.replace("\xd1", "N")
		html = html.replace("\xdc", "U")
		html = html.replace("\xf1", "n")
		html = html.replace("\x0a", "\n")

		html = html.replace("\xe1", "a")		
		html = html.replace("\xe9", "e")		
		html = html.replace("\xed", "i")		
		html = html.replace("\xf3", "o")				
		html = html.replace("\xfa", "u")


		html = html.replace("\xc1", "A")		
		html = html.replace("\xc9", "E")		
		html = html.replace("\xcd", "I")		
		html = html.replace("\xd3", "O")				
		html = html.replace("\xda", "U")
		server = smtplib.SMTP('smtp.gmail.com:587')
		msg = email.message.Message()
		msg['Subject'] = "Cierre de caja con diferencia"
		msg['From']=settings.EMAIL_HOST_USER
		msg['To']=settings.EMAIL_NOTIFICACIONES	
		password = settings.EMAIL_HOST_PASSWORD
		print(password)
		msg.add_header('Content-Type', 'text/html')
		msg.set_payload(html)		
		s = smtplib.SMTP('smtp.gmail.com:587')
		s.starttls()		
		# Login Credentials for sending the mail
		s.login(msg['From'], password)		
		s.sendmail(msg['From'], [msg['To']], msg.as_string())
	return 0



#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
@api_view(['GET'])
def api_consulta_corte_caja(request):
	
	respuesta=[]

	sucursal=Sucursal.objects.get(id=request.GET.get('id_sucursal'))
	c=request.GET.get('caja').upper()
	f=request.GET.get('fecha')

	fecha = parse_date(f)


	u=request.GET.get('usuario')
	user=User.objects.get(username__iexact=u)
	#usuario=User_2.objects.get(user=user)

	min_pub_date_time = datetime.combine(fecha, time.min) 
	max_pub_date_time = datetime.combine(fecha, time.max)  

	imp_fondo_inicial=0.00
	otros_ingresos=0.00
	cont_otros_ingresos=0
	retiros=0.00
	empenos=0.00
	cont_retiros=0
	total_movs=1
	caja_abierta=0#1 indica que la caja esta abiera; 0 indica que esta cerrada
	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),usuario=user,caja__iexact=c,sucursal=sucursal)
		imp_fondo_inicial=caja.importe

		print("caja")
		print(caja.usuario)
		#si no tiene fecha de cierre es porque la caja aun esta abierta.
		if caja.fecha_cierre ==None:
			caja_abierta=1

	except Exception as e:
		print(e)
		respuesta=[]
		respuesta.append({'estatus':0,'msj':'La caja indicada no existe.'})
		return Response(respuesta)

	#buscamos si el cajero tubo otros ingresos
	try:
		oi=Otros_Ingresos.objects.filter(ocaja = caja).aggregate(Sum('importe'))       
		cont_otros_ingresos=Otros_Ingresos.objects.filter(ocaja = caja).count()
		total_movs=total_movs+cont_otros_ingresos

		if oi["importe__sum"]!= None:
			otros_ingresos=oi["importe__sum"]

	except Exception as e:
		print(e)
		print("no tiene otros ingresos.")

	#le asignamos un token a la caja para poder manejar su cierre
	token=fn_genera_token()
	caja.token_cierre_caja=token
	caja.save()


	#buscamos las reimpresiones de boleta
	cont_rebol=Reg_Costos_Extra.objects.filter(caja=caja).count()
	sum_importe_rebol=Reg_Costos_Extra.objects.filter(caja=caja).aggregate(Sum('importe'))

	importe_rebol=0.00
	if sum_importe_rebol["importe__sum"]==None:
		importe_rebol=0.00
	else:
		importe_rebol=int(sum_importe_rebol["importe__sum"])

	#buscamos los retiros
	try:
		ret=Retiro_Efectivo.objects.filter(ocaja = caja,activo = 1).aggregate(Sum('importe'))
		cont_retiros=Retiro_Efectivo.objects.filter(ocaja = caja,activo = 1).count()
		total_movs=total_movs+cont_retiros #sumamos el total de retiros al total de movimientos
		if ret["importe__sum"]!=None:
			retiros=ret["importe__sum"]
	except Exception as e:
		print(e)
		print("No tiene otros ingresos.")

	try:
		emp=Boleta_Empeno.objects.filter(caja=caja).aggregate(Sum("mutuo_original"))
		cont_empenos=Boleta_Empeno.objects.filter(caja=caja).exclude(estatus__id = 2).count()
		total_movs=total_movs+cont_empenos
		if emp["mutuo_original__sum"]!=None:
			empenos=emp["mutuo_original__sum"]
	except Exception as e:
		print(e)
		print("No tiene empenños")


	#buscamos ingresos por ventas Granel
	cont_ventas=Venta_Granel.objects.filter(fecha_importe_venta__range=(min_pub_date_time,max_pub_date_time),caja=caja).count()
	imp_venta=Venta_Granel.objects.filter(fecha_importe_venta__range=(min_pub_date_time,max_pub_date_time),caja=caja).aggregate(Sum("importe_venta"))

	importe_ventas=0	
	if imp_venta["importe_venta__sum"]==None:
		importe_ventas=0.00
	else:
		importe_ventas=imp_venta["importe_venta__sum"]

	#buscamos ingresos por ventas piso
	cont_ventas=cont_ventas+Venta_Piso.objects.filter(caja=caja).count()

	imp_venta=Venta_Piso.objects.filter(caja=caja).aggregate(Sum("importe_venta"))	
	if imp_venta["importe_venta__sum"]==None:
		print("")
	else:
		importe_ventas=decimal.Decimal(importe_ventas)+decimal.Decimal(imp_venta["importe_venta__sum"])

	cont_ref_pg=0
	refrendos_pg=0.00

	cont_com_pg=0
	comisiones_pg=0.00

	cont_pc=0
	pago_capital=0.00

	cont_refrendos=0
	importe_refrendo=0.00

	importe_desemp=0.00
	cont_desemp=0

	cont_desemp=0
	importe_desemp=0.00

	importe_desemp=0.00
	cont_desemp=0		
	
	cont_ab_apartado = 0
	importe_apartado = 0

	cont_ab_apartado=Abono_Apartado.objects.filter(caja = caja).count()
	ia=Abono_Apartado.objects.filter(caja = caja).aggregate(Sum('importe'))

	if ia["importe__sum"] != None:
		importe_apartado = ia["importe__sum"]


	try:
		#buscamos el pago a comisiones PG
		abonos=Abono.objects.filter(caja=caja)#todos los abonos echos por la caja.

		est_refrendo=Tipo_Pago.objects.get(id=1)

		est_com_pg=Tipo_Pago.objects.get(id=2)

		est_ref_pg=Tipo_Pago.objects.get(id=3)



		
		for ab in abonos:
			rel_ab_pagos=Rel_Abono_Pago.objects.filter(abono=ab)#buscamos a que pago le pego cada refrendo


			#busamos si el abono afecto a refrendos.
			rel_ab_pagos_ref=Rel_Abono_Pago.objects.filter(abono=ab,pago__tipo_pago=est_refrendo)
			
			#si el abono afecto a pagos tipo refrendo, contamos en 1 el abono a refrendos
			if rel_ab_pagos_ref.exists():
				cont_refrendos=cont_refrendos+1

			#buscamos si el abono afecto a comision PG
			rel_ab_pagos_pg=Rel_Abono_Pago.objects.filter(abono=ab,pago__tipo_pago=est_com_pg)

			if rel_ab_pagos_pg.exists():
				cont_com_pg=cont_com_pg+1


			for p in rel_ab_pagos:
				if p.pago.tipo_pago==est_refrendo:#si afecto a refrendo acumulamos el importe.
					#cont_refrendos=cont_refrendos+1
					importe_refrendo=decimal.Decimal(importe_refrendo)+decimal.Decimal(p.pago.importe)

				if p.pago.tipo_pago==est_com_pg:#si afecto a comision pg acumulamos el importe.
					#cont_com_pg=cont_com_pg+1
					comisiones_pg=decimal.Decimal(comisiones_pg)+decimal.Decimal(p.pago.importe)

				if p.pago.tipo_pago==est_ref_pg:#si afecto a refrebdis pg acumulamos el importe.
					#cont_refrendos=cont_refrendos+1
					importe_refrendo=decimal.Decimal(importe_refrendo)+decimal.Decimal(p.pago.importe)

			#las boletas de plazo mensual se pagan en periodos			
			rap=Rel_Abono_Periodo.objects.filter(abono=ab)
			if rap.exists():
				cont_refrendos=cont_refrendos+1
			for x in rap:
				#cont_refrendos=cont_refrendos+1
				importe_refrendo=decimal.Decimal(importe_refrendo)+decimal.Decimal(x.periodo.importe)

			importe_refrendo=round(importe_refrendo)

			rel_ab_cap=Rel_Abono_Capital.objects.filter(abono=ab).exclude(capital_restante=0).aggregate(Sum("importe"))#buscamos si el abono afecto a capital
			cont_pc=cont_pc+Rel_Abono_Capital.objects.filter(abono=ab).exclude(capital_restante=0).count()

			if rel_ab_cap["importe__sum"]==None:
				pago_capital=pago_capital+0
			else:
				pago_capital=pago_capital+int(rel_ab_cap["importe__sum"])


			rel_desem=Rel_Abono_Capital.objects.filter(abono=ab)#.exclude(capital_restante__gte=0).aggregate(Sum("importe"))#buscamos si el abono afecto a capital
			#cont_desemp=cont_desemp+Rel_Abono_Capital.objects.filter(abono=ab).exclude(capital_restante__gte=0).count()


	
			for x in rel_desem:								
				
				if decimal.Decimal(x.capital_restante)==decimal.Decimal(0):					
					
					importe_desemp=decimal.Decimal(importe_desemp)+decimal.Decimal(x.importe)
					cont_desemp=int(cont_desemp)+1
					


			#if rel_desem["importe__sum"]==None:
			#	importe_desemp=importe_desemp+0
			#else:
			#	importe_desemp=importe_desemp+int(rel_desem["importe__sum"])
			

		




	except Exception as e:
		print(e)
		print("No se han registrado abonos.")


	
	

	total_movs=int(total_movs+cont_ab_apartado+cont_com_pg+refrendos_pg+cont_pc+cont_refrendos+cont_desemp+cont_rebol+cont_ventas)

	total_efectivo=0.00

	total_efectivo=decimal.Decimal(imp_fondo_inicial)+decimal.Decimal(importe_apartado)+decimal.Decimal(otros_ingresos)-decimal.Decimal(retiros)-decimal.Decimal(empenos)+decimal.Decimal(refrendos_pg)+decimal.Decimal(comisiones_pg)+decimal.Decimal(importe_refrendo)+decimal.Decimal(pago_capital)+decimal.Decimal(importe_desemp)+decimal.Decimal(importe_rebol)+decimal.Decimal(importe_ventas)

	caja.teorico_efectivo=total_efectivo
	caja.save()

	today = datetime.combine(datetime.now(), time.min) 
	fecha_caja = datetime.combine(caja.fecha, time.min) 

	today = datetime.strftime(today, '%Y-%m-%d')
	fecha_caja = datetime.strftime(fecha_caja, '%Y-%m-%d')

	dia_valido="1"

	diff=days_between(today,fecha_caja)


	#validamos que la caja sea del dia de hoy
	if diff!=0:
		dia_valido="0"

	respuesta=[]	

	f_otros_ingresos = otros_ingresos
	f_importe_refrendo = importe_refrendo
	f_comisiones_pg = comisiones_pg
	f_importe_desemp = importe_desemp
	f_pago_capital = pago_capital
	f_importe_rebol = importe_rebol
	f_importe_ventas = importe_ventas
	f_importe_apartado = importe_apartado
	f_retiros = retiros
	f_empenos = empenos
	f_total_efectivo = total_efectivo
	importe_ventas="{:0,.2f}".format(importe_ventas)
	importe_rebol="{:0,.2f}".format(importe_rebol)
	importe_desemp="{:0,.2f}".format(importe_desemp)
	pago_capital="{:0,.2f}".format(pago_capital)
	comisiones_pg="{:0,.2f}".format(comisiones_pg)
	importe_refrendo="{:0,.2f}".format(importe_refrendo)
	otros_ingresos="{:0,.2f}".format(otros_ingresos)
	importe_apartado="{:0,.2f}".format(importe_apartado)
	empenos = 	"$"+"{:0,.2f}".format(empenos)
	retiros = "{:0,.2f}".format(retiros)
	txt_total_efectivo = "{:0,.2f}".format(total_efectivo)
	respuesta.append({'cont_ab_apartado':cont_ab_apartado,'importe_apartado':importe_apartado,'nombre_cajero':caja.usuario.first_name+' '+caja.usuario.last_name,'estatus_guardado':caja.estatus_guardado,'dia_valido':dia_valido,'caja_abierta':caja_abierta,'token':str(token),'estatus':1,'fondo_inicial':str(imp_fondo_inicial),'cont_fondo_inicial':'1','otros_ingresos':str(otros_ingresos),'cont_otros_ingresos':str(cont_otros_ingresos),'retiros':str(retiros),'cont_retiros':str(cont_retiros),'total_movs':str(total_movs),'total_efectivo':str(total_efectivo),'real_efectivo':caja.real_efectivo,'empenos':str(empenos),'cont_empenos':str(cont_empenos),'cont_refrendos':str(cont_refrendos),'cont_com_pg':str(cont_com_pg),'cont_ref_pg':str(cont_ref_pg),'importe_refrendo':str(importe_refrendo),'comisiones_pg':str(comisiones_pg),'refrendos_pg':str(refrendos_pg),'cont_pc':cont_pc,		'pago_capital':pago_capital,"importe_desemp":importe_desemp,"cont_desemp":cont_desemp,"importe_rebol":importe_rebol,"cont_rebol":cont_rebol,'importe_ventas':importe_ventas,'cont_ventas':cont_ventas,"sucursal":caja.sucursal.sucursal,"txt_total_efectivo":txt_total_efectivo,"f_otros_ingresos":f_otros_ingresos,"f_importe_refrendo":f_importe_refrendo,"f_comisiones_pg":f_comisiones_pg,"f_pago_capital":f_pago_capital,"f_importe_desemp":f_importe_desemp,"f_importe_rebol":f_importe_rebol,"f_importe_ventas":f_importe_ventas,"f_importe_apartado":f_importe_apartado,"f_retiros":f_retiros,"f_empenos":f_empenos,"f_total_efectivo":f_total_efectivo})	
	
	#agregamos una segunda lina con la informacion guardada ne el corte de caja	
	respuesta.append({'comentario':caja.comentario,'centavos_10':caja.centavos_10,'centavos_50':caja.centavos_50,'pesos_1':caja.pesos_1,'pesos_2':caja.pesos_2,'pesos_5':caja.pesos_5,'pesos_10':caja.pesos_10,'pesos_20':caja.pesos_20,'pesos_50':caja.pesos_50,'pesos_100':caja.pesos_100,'pesos_200':caja.pesos_200,'pesos_500':caja.pesos_500,'pesos_1000':caja.pesos_1000,'diferencia':caja.diferencia,'real_efectivo':caja.real_efectivo})

	return Response(respuesta)

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************
@api_view(['GET'])
def api_cierra_caja(request):
	token=request.GET.get("token")
	
	user=User.objects.get(username=request.GET.get("username"));
	respuesta=[]
	try:
		caja=Cajas.objects.get(token_cierre_caja=request.GET.get("token"),fecha_cierre__isnull=True)	
		caja.fecha_cierre=datetime.now()
		caja.user_cierra_caja=user		
		caja.save()
		fn_envia_mail_diferencia_cierre_caja(caja)
		respuesta.append({"estatus":"1"})
	except Exception as e:
		print(e)
		respuesta.append({"estatus":"0","msj":"Error al cerrar la caja, comuniquese con el administrador del sistema"})
	return Response(respuesta)

	#*******************************************************************************************************************************************************
	#*¨**************************************************************************************************************************************************************

@api_view(['GET'])
def api_re_abre_caja(request):
	token=request.GET.get("token")
	respuesta=[]

	try:
		pub_date = date.today()
		min_pub_date_time = datetime.combine(pub_date, time.min) 
		max_pub_date_time = datetime.combine(pub_date, time.max) 
		#validamos si el usuario ya tiene caja abierta el dia de hoy.
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),fecha_cierre__isnull=True,usuario=caja.usuario)
		respuesta.append({"estatus":"0","msj":"El usuario ya cuenta con una caja abierta el dia de hoy, no puede abrir esta caja."})
	except:
		print("no tiene caja abierta")

	try:
		caja=Cajas.objects.get(token_cierre_caja=request.GET.get("token"))
		caja.fecha_cierre=None
		caja.user_cierra_caja=None
		caja.save()
		respuesta.append({"estatus":"1"})
	except Exception as e:
		print(e)
		respuesta.append({"estatus":"0","msj":"No se logro reabrir la caja, contacte al administrador del sistema."})


	return Response(respuesta)


#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

#*******************************************************************************************************************************************************
#*¨**************************************************************************************************************************************************************



def fn_nueva_caja(sucursal):
	pub_date = date.today()
	min_pub_date_time = datetime.combine(pub_date, time.min) 
	max_pub_date_time = datetime.combine(pub_date, time.max)  

	caja_siguiente=""
	#validamos la existencia de la caja A
	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),caja='A',sucursal=sucursal)
	except:
		#si no existe la caja A, es la que abriremos.
		caja_siguiente="A"
		return caja_siguiente

	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),caja='B',sucursal=sucursal)
	except:
		#si no existe la caja B, es la que abriremos.
		caja_siguiente="B"
		return caja_siguiente

	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),caja='C',sucursal=sucursal)
	except:
		#si no existe la caja B, es la que abriremos.
		caja_siguiente="C"
		return caja_siguiente

	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),caja='D',sucursal=sucursal)
	except:
		#si no existe la caja B, es la que abriremos.
		caja_siguiente="D"
		return caja_siguiente

	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),caja='E',sucursal=sucursal)
	except:
		#si no existe la caja B, es la que abriremos.
		caja_siguiente="E"
		return caja_siguiente


	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),caja='F',sucursal=sucursal)
	except:
		#si no existe la caja B, es la que abriremos.
		caja_siguiente="F"
		return caja_siguiente


	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),caja='G',sucursal=sucursal)
	except:
		#si no existe la caja B, es la que abriremos.
		caja_siguiente="G"
		return caja_siguiente


	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),caja='H',sucursal=sucursal)
	except:
		#si no existe la caja B, es la que abriremos.
		caja_siguiente="H"
		return caja_siguiente


	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),caja='I',sucursal=sucursal)
	except:
		#si no existe la caja B, es la que abriremos.
		caja_siguiente="I"
		return caja_siguiente


	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),caja='J',sucursal=sucursal)
	except:
		#si no existe la caja B, es la que abriremos.
		caja_siguiente="J"
		return caja_siguiente


	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),caja='K',sucursal=sucursal)
	except:
		#si no existe la caja B, es la que abriremos.
		caja_siguiente="K"
		return caja_siguiente



	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),caja='L',sucursal=sucursal)
	except:
		#si no existe la caja B, es la que abriremos.
		caja_siguiente="L"
		return caja_siguiente


	try:
		caja=Cajas.objects.get(fecha__range=(min_pub_date_time,max_pub_date_time),caja='M',sucursal=sucursal)
	except:
		#si no existe la caja B, es la que abriremos.
		caja_siguiente="M"
		return caja_siguiente

	caja_siguiente="M"
	return caja_siguiente





def fn_genera_token():
	token=""
	token=str(randint(0,9))	
	token=token+str(randint(0,9))	
	token=token+str(randint(0,9))	
	token=token+str(randint(0,9))	
	token=token+str(randint(0,9))	
	token=token+str(randint(0,9))	
	token=token+str(randint(0,9))	
	return token


#me hablo carmen para que corra estos procesos
#habiltar credito
#correr proceso de bloque de afiliada






		



	


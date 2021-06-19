from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from seguridad.models import *
from datetime import date, datetime, time,timedelta
import calendar
from django.db.models import Sum,Max
import decimal
from django.db.models import Min
from django.db import transaction
import math

GENERO_CHOICES = (
    ('1','HOMBRE'),
    ('2', 'MUJER'),
)

ESTADO_CIVIL_CHOICES = (
    ('1','SOLTERO'),
    ('2', 'CASADO'),
)

SI_NO=(
	('1','SI'),
	('2','NO'),
)

ESTATUS_ABONO = (
	('1','ACTIVO'),
	('2','CANCELADO'),
)

#al momendo de anunciar un producto para la venta piso, 
#se le aumenta un % sobre el avaluo, ese porcentaje es configurable en esta tabla.
#es por negocio
#solo debe existir un registro.
class Porcentaje_Sobre_Avaluo(models.Model):
	porcentaje=models.DecimalField(max_digits = 20,decimal_places = 2)#este es el procentaje para venta
	porcentaje_apartado=models.DecimalField(max_digits = 20, decimal_places = 2)#es el porcentaje para apartado

	#porcentaje=models.IntegerField()#este es el procentaje para venta
	#porcentaje_apartado=models.IntegerField()#es el porcentaje para apartado


class Tipo_Movimiento(models.Model):
	tipo_movimiento=models.CharField(max_length=50,null=False)
	naturaleza=models.CharField(max_length=20,null=False)

	def __str__(self):
		return self.tipo_movimiento


class Min_Apartado(models.Model):
	porc_min_1_mes=models.IntegerField()
	porc_min_2_mes=models.IntegerField()
	a_criterio_cajero = models.BooleanField( default = False);
	usuario_modifica = models.ForeignKey(User,on_delete = models.PROTECT,null = True,blank = True)

class Perfil(models.Model):
	perfil=models.CharField(max_length=30,null=False)

	def __str__(self):
		return str(self.id)+' '+self.perfil

#es la informacion general de la empresa.
#debe haeber sol un registro
class Empresa (models.Model):
	rfc = models.CharField(max_length = 13,default = '')
	nombre_empresa = models.CharField(max_length = 20,default = '')
	horario = models.CharField(max_length = 50,default = '')

#Solo puede haber un registro 
class Configuracion_Contenido_Impresion(models.Model):
	leyenda_final_venta = models.CharField(max_length = 200,default = '')

class Sucursal(models.Model):
	sucursal=models.CharField(max_length=100,null=False)
	calle=models.CharField(max_length=50,null=True,default='')
	codigo_postal=models.CharField(max_length=10,null=True,default='')
	numero_interior=models.IntegerField(default=0,null=True)
	numero_exterior=models.IntegerField(default=0,null=True)
	colonia=models.CharField(max_length=50,null=True,default='')
	ciudad=models.CharField(max_length=50,null=True,default='')
	estado=models.CharField(max_length=50,null=True,default='')
	pais=models.CharField(max_length=50,null=True,default='')
	telefono=models.CharField(max_length=10,null=True,default='')
	saldo = models.IntegerField(default=0)
	usuario_virtual = models.ForeignKey(User,on_delete = models.PROTECT,null = True,blank = True)
	

	def __str__(self):
		return self.sucursal

	def fn_abre_caja(self,importe_apertura,usuario_apertura):
		hoy = date.today()

		hoy_min = datetime.combine(hoy,time.min)
		hoy_max = datetime.combine(hoy,time.max)

		resp = []

		#validamos que la sucursal no tenga caja abierta		
		caja = Cajas.objects.filter(fecha_cierre__isnull = True,sucursal = self)
		if caja.exists():
			resp.append(False)			
			resp.append("La sucursal cuenta con caja abierta. Solo puede abrir una caja por sucursal.")
			return resp

		#buscamos el importe con el que cerro la ultima caja
		ultima_caja = Cajas.objects.filter(sucursal = self).aggregate(Max("id"))["id__max"]
		importe_ultima_caja = 0#si es la primera vez que se apertura caja el importe es cero, de lo contrario, se toma el importe con el que cerro anteriormente
		if ultima_caja != None: 
			importe_ultima_caja = Cajas.objects.get(id = int(ultima_caja)).teorico_efectivo

		if float(importe_apertura) != float(importe_ultima_caja) or float(importe_apertura) != self.saldo:
			resp.append(False)			
			resp.append("El importe con el que desea aperturar, es diferente al importe con el que cerro la ùltima caja.")
			return resp

		if self.usuario_virtual == None:
			resp.append(False)			
			resp.append("La sucursal no tiene asignado usuario virtual, contacte con el administrador del sistema.")
			return resp

		caja_abierta = Cajas.objects.filter(fecha__range = (hoy_min,hoy_max),sucursal = self,fecha_cierre__isnull = False)

		if caja_abierta.exists():
			resp.append(False)			
			resp.append("La caja de esta sucursal ya fue cerrada.")
			return resp

		tm = Tipo_Movimiento.objects.get(id=1)
		folio = fn_folios(tm,self)
		str_folio = fn_str_clave(folio)

		caja = Cajas()
		
		caja.folio = str_folio
		caja.tipo_movimiento = tm
		caja.sucursal = self		
		caja.usuario = self.usuario_virtual
		caja.importe = float(importe_apertura)
		caja.caja = "A"#como solo se puede aperturar una caja por sucursal, siempre sera la caja A
		caja.usuario_real_abre_caja = usuario_apertura
		caja.save()

		resp.append(True)	

		return resp
		
	#si no contamos con caja abierta, regresa None
	def fn_get_caja_abierta(self):
		hoy = date.today()
		hoy_min = datetime.combine(hoy,time.min)
		hoy_max = datetime.combine(hoy,time.max)

		try:
			#buscamos la caja abierta
			caja = Cajas.objects.get(fecha__range = (hoy_min,hoy_max),sucursal = self,fecha_cierre__isnull = True)
		except:
			caja = None

		return caja





	def fn_actualiza_porcentaje_mutuo(self,porcentaje_oro,porcentaje_plata,porcentaje_articulos_varios):

		#validamos que los valores sean enteros
		if type(porcentaje_oro) != type(0):
			return False

		if type(porcentaje_plata) != type(0):
			return False

		if type(porcentaje_articulos_varios) != type(0):
			return False

		if porcentaje_oro <= 0:
			return False

		if porcentaje_plata <= 0:
			return False

		if porcentaje_articulos_varios <= 0:
			return False			

		try:
			cpm = Configuracion_Porcentaje_Mutuo.objects.get(sucursal = self)
		except Exception as e:#si falla es porque aun no tiene configurada el porcentaje mutuo
			
			cpm = Configuracion_Porcentaje_Mutuo()
			cpm.sucursal = self

		cpm.porcentaje_oro = porcentaje_oro
		cpm.porcentaje_plata = porcentaje_plata
		cpm.porcentaje_articulos_varios = porcentaje_articulos_varios
		cpm.save()

		return True

	def fn_consulta_porcentaje_mutuo(self):
		try:
			return Configuracion_Porcentaje_Mutuo.objects.get(sucursal = self)
		except Exception as e:			
			return False

	#recibe el tipo de producto y regresa el interes que le corresponde a ese tipo de producto
	def fn_get_interes(self,tipo_producto):

		cpm = Configuracion_Interes_Empeno.objects.get(sucursal = self)

		#si es oro
		if tipo_producto == 1:
			return cpm.interes_oro
		elif tipo_producto == 2:
			return cpm.interes_plata
		elif tipo_producto == 3:
			return cpm.interes_prod_varios
		else:
			return 0


	#recibe como parametro el tipo de producto y regresa el porcentaje de almacenje que le corresponde a ese tipo de producto
	def fn_get_almacenaje(self,tipo_producto):
		cpm = Configuracion_Interes_Empeno.objects.get(sucursal = self)

		#si es oro
		if tipo_producto == 1:
			return cpm.almacenaje_oro
		elif tipo_producto == 2:
			return cpm.almacenaje_plata
		elif tipo_producto == 3:
			return cpm.almacenaje_prod_varios
		else:
			return 0

	#recibe como parametro el tipo de producto y regresa el porcentaje de IVA que le corresponde a ese tipo de producto
	def fn_get_iva(self,tipo_producto):
		cpm = Configuracion_Interes_Empeno.objects.get(sucursal = self)

		#si es oro
		if tipo_producto == 1:
			return cpm.iva_oro
		elif tipo_producto == 2:
			return cpm.iva_plata
		elif tipo_producto == 3:
			return cpm.iva_prod_varios
		else:
			return 0

	#funcion que recibe el mutuo y el tipo de producto para calcular el refrendo que le corresponde
	# considerando la sucursal en la que se encuentra. y la configuracion de la tabla Configuracion_Interes_Empeno
	# este se usa solo para la cotizacion, ya que para guardar el refrendo en la boleta se usa la funcion de el modelo Boleta Empeno
	def fn_calcula_refrendo(self,mutuo,tipo_producto):
		
		almacenaje = 0.00
		interes = 0.00
		iva=0.00
		refrendo = 0.00
		respuesta = []

		try:
			cie = Configuracion_Interes_Empeno.objects.get(sucursal = self)
		except:
			#el estatus cero es error al encontrar la configuracion de interes empeno
			respuesta.append({"estatus":"0","almacenaje":0,"interes":0,"iva":0,"refrendo":0})
			return respuesta

		if tipo_producto == 1 :#Oro

			p_almacenaje = cie.almacenaje_oro/100
			p_interes = cie.interes_oro/100
			p_iva  = cie.iva_oro/100

		elif tipo_producto == 2:#plata
			p_almacenaje = cie.almacenaje_plata/100
			p_interes = cie.interes_plata/100
			p_iva  = cie.iva_plata/100

		else:		

			p_almacenaje = cie.almacenaje_prod_varios /100
			p_interes = cie.interes_prod_varios /100
			p_iva  = cie.iva_prod_varios /100

		almacenaje = (mutuo * p_almacenaje)
		interes = (mutuo * p_interes)
		iva = ((almacenaje+interes) * p_iva)
		refrendo = round(almacenaje+interes+iva)
		respuesta.append({"estatus":"1","almacenaje":almacenaje,"interes":interes,"iva":iva,"refrendo":refrendo})
		
		return respuesta


	#funcion que recibe un rango de fechas y regresa el importe total de refrendos recibidos	
	def fn_get_total_refrendos(self,fecha_i,fecha_f):
		abonos = Abono.objects.filter(fecha__range = (fecha_i,fecha_f),sucursal = self)
		refrendo  = 0.00
		for a in abonos:
			#Buscamos los refrendos  de las boletas de plazo semanal.
			rap = Rel_Abono_Pago.objects.filter(abono = a)
			for r in rap:
				
				#si afecto a un refrendo o refrendo pg, lo contamos como refrendo				
				if r.pago.tipo_pago.id == 1 or r.pago.tipo_pago.id == 3:

					refrendo = decimal.Decimal(refrendo) + decimal.Decimal(r.pago.importe)

			#buscamos las boletas de plazo mensual
			rap = Rel_Abono_Periodo.objects.filter(abono = a)
			for r in rap:
				refrendo = decimal.Decimal(refrendo) + decimal.Decimal(r.periodo.importe)				

		return refrendo

	#funcion que recibe un rango de fecas y regresa el importe total de pagos a comision pg
	def fn_get_total_comision_pg(self,fecha_i,fecha_f):
		abonos = Abono.objects.filter(fecha__range = (fecha_i,fecha_f),sucursal = self)
		comision_pg  = 0.00
		for a in abonos:			
			rap = Rel_Abono_Pago.objects.filter(abono = a)
			for r in rap:				
				#Solo contamos los tipos de pagos comision pg
				if r.pago.tipo_pago.id == 2:
					comision_pg = decimal.Decimal(comision_pg) + decimal.Decimal(r.pago.importe)

		return comision_pg

	#funcion que recibe un rango de fechas y regresa el importe de costos extras.
	#al momento de crear esta rutina, solo existe el cobro reimpresion de boleta.
	def fn_get_total_costos_extras(self,fecha_i,fecha_f):
		rce = Reg_Costos_Extra.objects.filter(fecha__range = (fecha_i,fecha_f),caja__sucursal = self).aggregate(Sum("importe"))

		total_costo_extra = 0

		if rce["importe__sum"] != None:
			total_costo_extra = rce["importe__sum"]

		return decimal.Decimal(total_costo_extra)

	#funcin que recibe un rango de fechas y regresa la ganancia de las ventas.
	#importe_venta - mutuo_real = ganancia el ventas.
	def fn_get_ganancia_ventas(self,fecha_i,fecha_f):
		importe_mutuo = 0
		importe_venta = 0

		im = Venta_Piso.objects.filter(sucursal = self, fecha__range = (fecha_i,fecha_f)).aggregate(Sum("importe_mutuo"))
		if im["importe_mutuo__sum"]!= None:
			importe_mutuo = im["importe_mutuo__sum"]

		img = Venta_Granel.objects.filter(sucursal = self, fecha__range = (fecha_i,fecha_f)).aggregate(Sum("importe_mutuo"))
		if img["importe_mutuo__sum"]!= None:
			importe_mutuo = decimal.Decimal(importe_mutuo)+ decimal.Decimal(img["importe_mutuo__sum"])



		iv = Venta_Piso.objects.filter(sucursal = self, fecha__range = (fecha_i,fecha_f)).aggregate(Sum("importe_venta"))
		if iv["importe_venta__sum"]!= None:
			importe_venta = iv["importe_venta__sum"]	


		ivg = Venta_Granel.objects.filter(sucursal = self, fecha__range = (fecha_i,fecha_f)).aggregate(Sum("importe_venta"))
		if ivg["importe_venta__sum"]!= None:
			importe_venta = decimal.Decimal(importe_venta) + decimal.Decimal(ivg["importe_venta__sum"])

		return decimal.Decimal(importe_venta) - decimal.Decimal(importe_mutuo)

	def fn_get_retiros(self,fecha_i,fecha_f):

		ret=Retiro_Efectivo.objects.filter(sucursal=self,fecha__range=(fecha_i,fecha_f),activo = 1).aggregate(Sum("importe"))

		importe_retiros=0.00					
		if ret["importe__sum"]!=None:
			importe_retiros=ret["importe__sum"]

		return importe_retiros			

#esta configuracion es por sucursal.
class Porcentaje_Comision_PG(models.Model):	
	porcentaje = models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	usuario = models.ForeignKey(User,on_delete = models.PROTECT,null=True,blank=True) #el usuario que actualiza por ultimavez

class Concepto_Retiro(models.Model):
	concepto = models.CharField(max_length = 40,null = False)
	sucursal = models.ForeignKey(Sucursal,on_delete = models.PROTECT,blank=True,null=True,related_name = "sucursal_origen")
	importe_maximo_retiro = models.PositiveIntegerField()	
	fecha_alta = models.DateTimeField(default = timezone.now)
	fecha_modificacion = models.DateTimeField(default = timezone.now)
	usuario_ultima_mod = models.ForeignKey(User,on_delete = models.PROTECT)
	activo = models.CharField(choices=SI_NO,max_length=2,default="SI")
	sucursal_destino = models.ForeignKey(Sucursal,on_delete = models.PROTECT,null = True,blank = True,related_name = "sucursal_destino")#en caso de que sea un concepto para traspaso, esta es la sucursal a la que va dirigido

	def __str__(self):
		return str(self.id)+' '+self.concepto+' '+str(self.importe_maximo_retiro)

	def fn_nuevo_concepto(id_sucursal,id_usuario,importe,concepto,id_sucursal_destino):	

		try:
			if concepto == "":
				return False

			if int(importe) < 0 or int(importe) == 0:
				return False

			sucursal = Sucursal.objects.get(id = int(id_sucursal))
			sucursal_destino = None
			if Sucursal.objects.filter(id = int(id_sucursal_destino)).exists():
				sucursal_destino = Sucursal.objects.get(id = int(id_sucursal_destino))	

			usuario = User.objects.get(id = int(id_usuario))
			Concepto_Retiro.objects.create(activo = 1, concepto = concepto.upper(),sucursal = sucursal,importe_maximo_retiro = importe,usuario_ultima_mod = usuario,sucursal_destino = sucursal_destino)
			return True
		except Exception as e:
			print(e)
			return False

	def fn_get_conceptos(id_sucursal):

		return Concepto_Retiro.objects.filter(sucursal__id = int(id_sucursal),activo="1")

	def fn_delete_concepto(id_concepto,id_usuario):
		try:
			usuario = User.objects.get(id = int(id_usuario))

			concepto = Concepto_Retiro.objects.get(id = int(id_concepto))
			concepto.activo = 2
			concepto.usuario_ultima_mod = usuario
			concepto.fecha_modificacion = datetime.now()
			concepto.save()

			return True;
		except Exception as e:
			
			return False;

	def fn_update_importe_maximo_retiro(id_concepto,importe_maximo_retiro,id_usuario):
		try:

			if int(importe_maximo_retiro) < 0:
				return False

			if int(importe_maximo_retiro) == 0:
				return False
				
			usuario = User.objects.get(id = int(id_usuario))
			concepto = Concepto_Retiro.objects.get(id=int(id_concepto))
			concepto.importe_maximo_retiro = importe_maximo_retiro
			concepto.usuario_ultima_mod=usuario
			concepto.fecha_modificacion=datetime.now()
			concepto.save()
			
			return True
		except Exception as e:			
			print(e)
			return False

	def fn_saldo_concepto(self):		
		#obtenemos la fecha inicial y fecha final del mes en curso
		fecha = timezone.now()
		rangos_fecha = calendar.monthrange(fecha.year , fecha.month)

		mes = rangos_fecha[1]
		fecha_inicial = datetime(int(fecha.year),int(fecha.month),1,0,0)
		fecha_final = datetime(fecha.year,fecha.month,mes,0,0)
		fecha_inicial = datetime.combine(fecha_inicial,time.min)
		fecha_final = datetime.combine(fecha_final,time.max)

		#obtenemos todos los retiros pertenecientes al consepto consultado
		re = Retiro_Efectivo.objects.filter(concepto = self,fecha__range = (fecha_inicial,fecha_final)).aggregate(Sum("importe"))
		
		total_retirado = 0
		if re["importe__sum"] != None:
			total_retirado = re["importe__sum"]
		else:
			total_retirado = 0

		#retornamos la diferencia entre el importe maximo y el total retirado
		#para saber cuando saldo le queda a este concepto
		return int(self.importe_maximo_retiro) - int(total_retirado)

class Control_Folios(models.Model):
	folio=models.IntegerField(default=0)
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento,on_delete=models.PROTECT)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)
	
	def __str__(self):
		return self.sucursal.sucursal+' '+self.tipo_movimiento.tipo_movimiento

	class Meta:
		unique_together=('tipo_movimiento','sucursal',)	

class Sucursales_Regional(models.Model):
	user=models.ForeignKey(User,on_delete=models.PROTECT)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)

	def __str__(self):
		return self.user.username + ' ' + self.sucursal.sucursal

#esta tabla es un complemento de la tabla user de django.
class User_2(models.Model):
	user=models.ForeignKey(User,on_delete=models.PROTECT,related_name = "usuario_sistema")
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)
	perfil=models.ForeignKey(Perfil,on_delete=models.PROTECT)
	sesion=models.IntegerField(blank=True,null=True)
	usuario_alta = models.ForeignKey(User,on_delete = models.PROTECT,related_name = "usuario_alta_usuario",blank = True,null = True)
	fecha_alta = models.DateTimeField(default = timezone.now())
	usuario_modifica = models.ForeignKey(User,on_delete = models.PROTECT,related_name = "usuario_modifica_usuario",blank = True,null = True)
	fecha_modificacion = models.DateTimeField(default = timezone.now())

	class Meta:
		unique_together=('user',)

	def __str__(self):
		return self.user.username

	def fn_is_logueado(usuario):
		#si no esta logueado mandamos al login
		if not usuario.is_authenticated:
			return None
		
		#Para que un usuario sea vañido, adebas de estar creado en la tabla User
		#tambien debe tener informacion en la tabla User_2
		try:
			user_2=User_2.objects.get(user=usuario)
		except Exception as e:							
			return None

		return user_2

	#funcion para validar si el usuario tiene caja abierta,
	#en caso de tenerle regresa un objeto de la caja
	#en caso de que no, regresa None
	def fn_tiene_caja_abierta(self):
		try:
			hoy_min = datetime.combine(date.today(),time.min)
			hoy_max = datetime.combine(date.today(),time.max)
			#validamos si el usuaario tiene caja abierta para mostrarla en el encabezado.
			return Cajas.objects.get(fecha__range = (hoy_min,hoy_max),fecha_cierre__isnull = True,usuario = self.user)			
		except Exception as e:
			print(e)
			return None
			
	def fn_alta_usuario(user_name,first_name,last_name,id_sucursal,id_perfil,id_usuario_alta):
		resp = []
		if user_name == "" or user_name == None:
			resp.append(False)
			resp.append("El nombre de usuario es requerido.")
			return resp

		try:
			sucursal = Sucursal.objects.get(id = id_sucursal)
		except:
			resp.append(False)
			resp.append("Debe indicar una sucursal valida.")
			return resp

		try:
			Perfil.objects.get(id = id_perfil)
		except:
			resp.append(False)
			resp.append("Debe indicar un perfil valido.")
			return resp


		usuario = User.objects.filter(username = user_name)

		if usuario.exists():
			resp.append(False)
			resp.append("El nombre de usuario indicado ya existe.")
			return resp


		try:
			usuario_alta = User.objects.get(id = int(id_usuario_alta))
			usuario = User()
			usuario.username = user_name
			usuario.first_name = first_name
			usuario.last_name = last_name
			usuario.is_staff = True
			usuario.is_active = True
			usuario.save()

			user_2 = User_2()
			user_2.user = usuario
			user_2.sucursal = Sucursal.objects.get(id = int(id_sucursal))

			user_2.perfil = Perfil.objects.get(id = int(id_perfil))
			user_2.usuario_alta = usuario_alta
			user_2.save()

			resp.append(True)
			resp.append("El usuario se creo correctamente.")
		except Exception as e:
			print(e)
			resp.append(False)
			resp.append("Error al crear el usuario, intente nuevamente.")
			return resp

		return resp


	def fn_edita_usuario(user_name,first_name,last_name,id_sucursal,id_perfil,id_usuario_alta,activo):
		resp = []
		if user_name == "" or user_name == None:
			resp.append(False)
			resp.append("El nombre de usuario es requerido.")
			return resp



		try:
			sucursal = Sucursal.objects.get(id = id_sucursal)
		except:
			resp.append(False)
			resp.append("Debe indicar una sucursal valida.")
			return resp

		try:
			Perfil.objects.get(id = id_perfil)
		except:
			resp.append(False)
			resp.append("Debe indicar un perfil valido.")
			return resp


		try:
			usr_modifica = User.objects.get(id = int(id_usuario_alta))

			usr_a_modificar = User.objects.get(username = user_name)
			
			u2 = User_2.objects.get(user = usr_a_modificar)

			if u2.fn_tiene_caja_abierta() != None:
				resp.append(False)
				resp.append("El usuario no puede ser modificado ya que cuenta con caja abierta.")
				return resp


			usr_a_modificar.first_name = first_name
			usr_a_modificar.last_name = last_name
			
			if activo == 0:
				usr_a_modificar.is_active = False
			else:				
				usr_a_modificar.is_active = True

			usr_a_modificar.save()

			user_2 = User_2.objects.get(user = usr_a_modificar)
			user_2.sucursal = Sucursal.objects.get(id = int(id_sucursal))
			user_2.perfil = Perfil.objects.get(id = int(id_perfil))
			user_2.usuario_modifica = usr_modifica
			user_2.fecha_modificacion = timezone.now()

			user_2.save()

			resp.append(True)
			resp.append("El usuario actualizo correctamente.")
		except Exception as e:
			print(e)
			resp.append(False)
			resp.append("Error al actualizar el usuario, intente nuevamente.")
			return resp

		return resp

	def fn_agrega_acceso_a_vista(self,id_menu,id_usuario_asigna):
	
		resp = []
		if not self.user.is_active:
			resp.append(False)
			resp.append("El usuario esta inactivo, no puede modificar sus permisos.")
			return resp

		try:
			menu = Menu.objects.get( id = id_menu)			
		except Exception as e:			
			print(e)
			resp.append(False)
			resp.append("La opción que intenta agregar no existe o no es valida.")
			return resp

		# Si el usuario ya tiene el permiso asignado, unicamente confirmamos que ya fue asignado
		# para refrescar la pantalla.
		try:
			Permisos_Usuario.objects.get(usuario = self.user,opcion_menu = Menu.objects.get(id = id_menu))			
			resp.append(True)
			resp.append("Se actualizo correctamente.")
			return resp
		except:
			pass
		
	
			
		try:
			pu = Permisos_Usuario()
			pu.usuario = self.user
			pu.opcion_menu = Menu.objects.get(id = id_menu)
			pu.usuario_otorga = User.objects.get(id = id_usuario_asigna)
			pu.save()
		except Exception as e:
			print(e)
			resp.append(False)
			resp.append("Error al actualizar los permisos..")
			return resp
		

		resp.append(True)
		resp.append("Se actualizo correctamente.")
		return resp

	def fn_remover_acceso_a_vista(self,id_menu):
		resp = []
		if not self.user.is_active:
			resp.append(False)
			resp.append("El usuario esta inactivo, no puede modificar sus permisos.")
			return resp

		#si la opcion que intentamos remover no existe, no importa
		#confirmaoms que ya se removio.
		try:
			menu = Menu.objects.get( id = id_menu)			
		except Exception as e:			
			print(e)
			resp.append(True)
			resp.append("Se actualizo correctamente.")
			return resp

		#removemos el permiso
		Permisos_Usuario.objects.filter(usuario = self.user,opcion_menu = Menu.objects.get(id = id_menu)).delete()

		resp.append(True)
		resp.append("Se actualizo correctamente.")

		return resp

	#regresa true cuando tienepermiso
	#regresa false cuando no tiene permiso
	def fn_tiene_acceso_a_vista(self,id_menu):
		
		try:
			Permisos_Usuario.objects.get(usuario = self.user,opcion_menu = Menu.objects.get(id = id_menu) )
		except:
			
			return False		
		
		return True


	###regresa una lista con todos los permsos del usuario
	###se usa para laopcion "administra permisos de usuario"
	###para cargar de inicio los permisos que ya tiene el usuario.
	def fn_consulta_permisos(self):
		resp = []
		permisos = Permisos_Usuario.objects.filter(usuario = self.user)
		for p in permisos:
			resp.append(p.opcion_menu.id)
		return resp



class Control_Folios(models.Model):
	folio=models.IntegerField(null=False)
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento,on_delete=models.PROTECT)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)


class Cajas(models.Model):
	folio=models.CharField(max_length=7,null=True)
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento,on_delete=models.PROTECT)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)
	fecha=models.DateTimeField(default=timezone.now)
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
	importe=models.IntegerField(default=0)
	caja=models.CharField(max_length=1,null=False)
	real_tarjeta=models.IntegerField(default=0)
	real_efectivo=models.IntegerField(default=0)
	teorico_tarjeta=models.IntegerField(default=0)
	teorico_efectivo=models.IntegerField(default=0)
	diferencia=models.IntegerField(default=0)
	fecha_cierre=models.DateTimeField(null=True)
	centavos_10=models.IntegerField(default=0)
	centavos_50=models.IntegerField(default=0)
	pesos_1=models.IntegerField(default=0)
	pesos_2=models.IntegerField(default=0)
	pesos_5=models.IntegerField(default=0)
	pesos_10=models.IntegerField(default=0)
	pesos_20=models.IntegerField(default=0)
	pesos_50=models.IntegerField(default=0)
	pesos_100=models.IntegerField(default=0)
	pesos_200=models.IntegerField(default=0)
	pesos_500=models.IntegerField(default=0)
	pesos_1000=models.IntegerField(default=0)
	token_cierre_caja=models.IntegerField(null=True)
	comentario=models.TextField(default='')
	user_cierra_caja=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user",blank = True,null=True)
	usuario_real_abre_caja = models.ForeignKey(User,on_delete = models.PROTECT,null = True,blank = True,related_name = "usuario_real_abre_caja")
	estatus_guardado=models.IntegerField(default=0)#cuando esta cero es que nunca se ha guardado informacion de cierre de caja, por lo tanto 
												   #no debemos mostrarle el boton de cierre de caja.
												   #cuando es 1, es que ya se ha guardado al menos una vez, y ya podemos mostrar el boton de cerrar caja


	def __str__(self):
		estatus="CERRADA"
		if self.fecha_cierre==None:
			estatus="Abierta"

		return str(self.fecha)+' '+estatus

class Otros_Ingresos(models.Model):
	folio = models.CharField(max_length=7,null=True)
	tipo_movimiento = models.ForeignKey(Tipo_Movimiento,on_delete=models.PROTECT)
	sucursal = models.ForeignKey(Sucursal,on_delete=models.PROTECT)
	fecha = models.DateTimeField(default=timezone.now)
	usuario = models.ForeignKey(User,on_delete=models.PROTECT) #
	importe = models.IntegerField(default=0, validators=[MinValueValidator(Decimal('1'))])
	comentario = models.CharField(max_length=200,default='')
	caja = models.CharField(max_length=1,null=True)
	activo = models.CharField(choices = SI_NO,default = 1, max_length=2)
	ocaja = models.ForeignKey(Cajas,on_delete = models.PROTECT,null = True,blank = True)


class Retiro_Efectivo(models.Model):
	folio=models.CharField(max_length = 7,null = True)
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento,on_delete = models.PROTECT)
	sucursal=models.ForeignKey(Sucursal,on_delete = models.PROTECT)
	fecha=models.DateTimeField(default = timezone.now)
	usuario=models.ForeignKey(User,on_delete = models.PROTECT,related_name = "usuario_alta")
	importe=models.IntegerField(default = 0, validators = [MinValueValidator(Decimal('1'))])
	comentario=models.TextField(default = '',max_length = 100)
	caja=models.CharField(max_length = 1,null = True)
	token=models.IntegerField()
	concepto = models.ForeignKey(Concepto_Retiro,on_delete = models.PROTECT,blank = True,null = True)
	#no requerimos fecha de cancelacion ya que solo se puede cancelar el dia en que se genera.
	usuario_cancela = models.ForeignKey(User,on_delete = models.PROTECT,null = True, blank = True,related_name = 'usuario_cancela')
	activo = models.CharField(choices = SI_NO,default = 1, max_length=2)
	ocaja = models.ForeignKey(Cajas,on_delete = models.PROTECT,null = True,blank = True)

	def fn_cancela_retiro(self,id_usuario_cancela,comentario_cancelacion):
		try:
			self.importe = 0
			self.comentario = comentario_cancelacion
			self.usuario_cancela = User.objects.get(id = int(id_usuario_cancela))
			self.activo = 2# no activo
			self.save()
			return True
		except:
			return False


#tabla de traspasos
class Traspaso_Entre_Sucursales(models.Model):
	retiro = models.ForeignKey(Retiro_Efectivo,on_delete = models.PROTECT)
	ingreso = models.ForeignKey(Otros_Ingresos,on_delete = models.PROTECT)
	visto = models.BooleanField(default=True)#Cuando se hace un traspaso, le lleva la notificacion a la sucursal destino, para notificarle que ha recibido dineros


class Token(models.Model):
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento,on_delete=models.PROTECT)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)
	caja=models.CharField(max_length=1,null=True)
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
	token=models.IntegerField()
	fecha=models.DateTimeField(default=timezone.now)
	aux_1 = models.IntegerField(null = True,blank = True)

class Tipo_Producto(models.Model):
	tipo_producto=models.CharField(max_length=100,null=False)

	def __str__(self):
		return self.tipo_producto

class Linea(models.Model):
	tipo_producto=models.ForeignKey(Tipo_Producto,on_delete=models.PROTECT)
	linea=models.CharField(max_length=100,null=False)

	def __str__(self):
		return self.linea
	class Meta:
		# sort by "fecha" in descending order unless
		# overridden in the query with order_by()
		ordering = ['linea']

class Sub_Linea(models.Model):
	linea=models.ForeignKey(Linea,on_delete=models.PROTECT)
	sub_linea=models.CharField(max_length=100,null=False)

	def __str__(self):
		return self.sub_linea

	class Meta:
		# sort by "fecha" in descending order unless
		# overridden in the query with order_by()
		ordering = ['sub_linea']


class Marca(models.Model):	
	marca=models.CharField(max_length=100,null=False)

	def __str__(self):
		return self.marca
	class Meta:
		# sort by "fecha" in descending order unless
		# overridden in the query with order_by()
		ordering = ['marca']


class Tipo_Kilataje(models.Model):
	tipo_kilataje=models.CharField(max_length=10,null=False)


class Costo_Kilataje(models.Model):	
	tipo_producto = models.ForeignKey(Tipo_Producto,on_delete=models.PROTECT,blank=True,null=False)
	kilataje = models.CharField(max_length=10,null=False)
	avaluo = models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	tipo_kilataje = models.ForeignKey(Tipo_Kilataje,on_delete=models.PROTECT,blank=True,null=True)
	activo = models.CharField(max_length=1,default="S")
	
	def __str__(self):
		return self.tipo_producto.tipo_producto+' '+self.kilataje+' $'+str(self.avaluo)

	#con la finalidad de poder saber cual el importe que tenia el kilataje
	#al momento de haer un empeño, no se edita, mas bien se desactiva el primero
	# y se crea uno nuevo con el nuevo importe.
	@transaction.atomic
	def fn_actualiza_kilataje(self,nuevo_importe):
		try:
			#creamos un kilataje igual pero con diferente precio
			Costo_Kilataje.objects.create(tipo_producto=self.tipo_producto,kilataje=self.kilataje,avaluo=nuevo_importe,tipo_kilataje=self.tipo_kilataje)
			#desactivamos el actual kilataje
			self.activo="N"
			self.save()
			return True
		except:
			transaction.set_rollback(True)
			return False

class Empenos_Temporal(models.Model):
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
	tipo_producto=models.ForeignKey(Tipo_Producto,on_delete=models.PROTECT)
	linea=models.ForeignKey(Linea,on_delete=models.PROTECT)
	sub_linea=models.ForeignKey(Sub_Linea,on_delete=models.PROTECT)	
	marca=models.ForeignKey(Marca,on_delete=models.PROTECT)
	descripcion=models.CharField(max_length=50,null=False)
	avaluo=models.IntegerField()
	mutuo_sugerido=models.IntegerField()
	mutuo=models.IntegerField()
	observaciones=models.TextField(null=True,blank=True)

	def get_mutuo_temporal(usuario):
		et_oro = Empenos_Temporal.objects.filter(usuario = usuario,tipo_producto__id = 1)		
		et_plata = Empenos_Temporal.objects.filter(usuario = usuario,tipo_producto__id = 2)		
		et_varios = Empenos_Temporal.objects.filter(usuario = usuario,tipo_producto__id = 3)		

		lista = []
		mutuo_oro = 0.00
		if et_oro.exists():
			mutuo_oro = et_oro.aggregate(Sum("mutuo"))["mutuo__sum"]

		mutuo_plata = 0.00
		if et_plata.exists():
			mutuo_plata = et_plata.aggregate(Sum("mutuo"))["mutuo__sum"]

		mutuo_varios = 0.00
		if et_varios.exists():
			mutuo_varios = et_varios.aggregate(Sum("mutuo"))["mutuo__sum"]


		lista.append({"mutuo_oro":mutuo_oro,"mutuo_plata":mutuo_plata,"mutuo_varios":mutuo_varios})

		return lista



	
class Joyeria_Empenos_Temporal(models.Model):
	empeno_temporal=models.ForeignKey(Empenos_Temporal,on_delete=models.PROTECT)
	costo_kilataje=models.ForeignKey(Costo_Kilataje,on_delete=models.PROTECT)
	peso=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)

	class Meta:
		unique_together=('empeno_temporal',)

class Plazo(models.Model):
	plazo=models.CharField(max_length=30,null=False)

	def __str__(self):
		return self.plazo

class Cliente(models.Model):
	nombre=models.CharField(max_length = 50,null = False)
	apellido_p=models.CharField(max_length = 50,null = False)
	apellido_m=models.CharField(max_length = 50,default = '',null = True)
	genero=models.CharField(choices=GENERO_CHOICES,max_length=30)
	estado_civil=models.CharField(choices=ESTADO_CIVIL_CHOICES,max_length=30)
	codigo_postal=models.CharField(max_length=10,null=True,default='')
	calle=models.CharField(max_length=50,null=True,default='')
	numero_interior=models.IntegerField(null=True,default=0)
	numero_exterior=models.IntegerField(null=True,default=0)
	colonia=models.CharField(max_length=50,null=True,default='')
	ciudad=models.CharField(max_length=50,null=True,default='')
	estado=models.CharField(max_length=50,null=True,default='')
	pais=models.CharField(max_length=50,null=True,default='')
	telefono_fijo=models.CharField(max_length=10,null=True,default='')
	telefono_celular=models.CharField(max_length=10,null=False)
	usuario=models.ForeignKey(User,on_delete=models.PROTECT,blank=True,null=True)
	fecha=models.DateTimeField(default=timezone.now)
	nombre_completo = models.CharField (max_length = 100,null = True,blank = True)

	def __str__(self):
		return self.nombre+' '+self.apellido_p+' '+self.apellido_m

	def fn_actualiza_nombre_completo():
		clientes = Cliente.objects.filter(nombre_completo = None) or Cliente.objects.filter(nombre_completo = "")

		for c in clientes:
			apellido_m = ""
			apellido_p = ""
			nombre = ""

			if c.nombre != None:
				nombre = c.nombre.upper()

			if c.apellido_m != None:
				apellido_m = c.apellido_m.upper()

			if c.apellido_p != None:
				apellido_p = c.apellido_p.upper()

			c.nombre_completo = nombre + ' ' +apellido_p + ' ' + apellido_m 
			c.save()
			
	def save(self, *args, **kwargs):
		self.nombre = (self.nombre).upper()
		self.apellido_p = (self.apellido_p).upper()
		self.apellido_m = (self.apellido_m).upper()
		return super(Cliente, self).save(*args, **kwargs)

class Estatus_Boleta(models.Model):
	estatus=models.CharField(max_length=20,null=False)
	nombre_corto=models.CharField(max_length=2,null=False)

	def __str__(self):
		return self.estatus+' '+self.nombre_corto

class Boleta_Empeno(models.Model):
	folio=models.IntegerField(null=False)
	tipo_producto=models.ForeignKey(Tipo_Producto,on_delete=models.PROTECT)
	caja=models.ForeignKey(Cajas,on_delete=models.PROTECT,blank=True,null=True)
	usuario=models.ForeignKey(User,on_delete=models.PROTECT,related_name = "usuario_empena")
	avaluo=models.IntegerField()
	mutuo=models.IntegerField()	#este campo se ira actualizando cuando se abona a capital
	fecha=models.DateTimeField(default=timezone.now)
	fecha_vencimiento=models.DateTimeField()
	cliente=models.ForeignKey(Cliente,on_delete=models.PROTECT)
	nombre_cotitular=models.CharField(max_length=20,default='NA')
	apellido_p_cotitular=models.CharField(max_length=20,default='NA')
	apellido_m_cotitular=models.CharField(max_length=20,default='NA')
	plazo=models.ForeignKey(Plazo,on_delete=models.PROTECT)
	refrendo=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	estatus=models.ForeignKey(Estatus_Boleta,on_delete=models.PROTECT,default=1,related_name = "estatus_b")
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT,blank=True,null=True)
	mutuo_original=models.IntegerField(default=0)	#este campo no se actualiza, nos sirve para saber cual fue el mutuo original de la boleta.
	fecha_vencimiento_real=models.DateTimeField(null=True,blank=True)#cuando la fecha de vencimiento cai en dia de asueto, la fecha de vencimienot se recorre un dia, esta fecha nos indica cual es la fecha de vencimiento real para calcular el las futuras fechas de vencimiento.
	almacenaje = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0)
	interes = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0)
	iva = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0)
	fecha_vencimiento_anterior = models.DateTimeField(null = True, blank = True)
	estatus_anterior = models.ForeignKey(Estatus_Boleta,on_delete = models.PROTECT, related_name = "estatus_anterior",null = True,blank = True)
	fecha_vencimiento_real_anterior = models.DateTimeField(null = True, blank = True)
	precio_venta_fijo = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0 ) #Cuando el precio de venta que se calcula en base a la configuracion de la tabla Porcentaje_Sobre_Avaluo
	#																					     no es el correcto, se establece un precio fijo.		
	usuario_establece_precio_fijo = models.ForeignKey(User,on_delete = models.PROTECT,null=True,blank = True,related_name = "usuario_establece_precio_fijo")																							 	
	usuario_cancela = models.ForeignKey(User,on_delete = models.PROTECT,null = True,blank = True)

	@classmethod
	def nuevo_empeno(self,sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus,folio,tm):

		boleta = self.objects.create(folio = folio,tipo_producto = tp,caja = caja,usuario = usuario,avaluo = avaluo,mutuo = mutuo,fecha = timezone.now(),fecha_vencimiento = fecha_vencimiento,cliente = cliente,nombre_cotitular = nombre_cotitular,apellido_p_cotitular = apellido_paterno,apellido_m_cotitular = apellido_materno,plazo = plazo,sucursal = sucursal,mutuo_original = mutuo,fecha_vencimiento_real = fecha_vencimiento_real,estatus = estatus,almacenaje =  sucursal.fn_get_almacenaje(tp.id), interes = sucursal.fn_get_interes(tp.id),iva = sucursal.fn_get_iva(tp.id))
				
		return boleta	
			
	def forzar_desempeno(self,importe_desempeno):

		if int(importe_desempeno) < 0:
			return [False,"El importe debe ser mayor a cero."]

		# validacion 1: Validamos que la boleta este en estatus almoneda o remate
		if  self.estatus.id != 3 and self.estatus.id != 5:
			return [False,"La boleta debe estar en estatus Almoneda o Remate"]

		if self.plazo.id != 2:
			return [False,"Esta opciones solo esta disponible para boletas de plazo semanal"]

		try:
			with transaction.atomic():
				# Si cuenta con comisiones de PG sin pagar, las ponemos en cero
				pagos = Pagos.objects.filter(boleta = self,tipo_pago__id = 2,pagado = "N")
				for p in pagos:
					p.importe = 0
					p.save()

				# dividimo el nuevo importe para desempeno entre el numero de pagos pendientes
				pagos = Pagos.objects.filter(boleta = self,pagado = "N").exclude(importe = 0)
				nvo_importe = int(importe_desempeno/pagos.count())
				if nvo_importe == 0:	
					nvo_importe = 1

				for p in pagos:
					p.importe = nvo_importe
					p.save()
				return [True,""]
		except:
			transaction.set_rollback(True)
			return [False,"Error al actualizar la información."]


	#funcion que calcula el refrendo de los proximos pagos de una boleta consderando el mutuo actual y los porcentajes de interes
	#que se tenian al momento de hacer el empeño.	
	def fn_calcula_refrendo(self):
		
		p_almacenaje = decimal.Decimal(self.almacenaje)/decimal.Decimal(100)
		p_interes = decimal.Decimal(self.interes)/decimal.Decimal(100)
		p_iva = decimal.Decimal(self.iva)/decimal.Decimal(100)

		almacenaje = 0.00
		interes = 0.00
		iva=0.00
		refrendo = 0.00

		respuesta = []

		almacenaje = (decimal.Decimal(self.mutuo) * p_almacenaje)
		interes = (decimal.Decimal(self.mutuo) * p_interes)
		iva = ((almacenaje+interes) * p_iva)
		refrendo = round(almacenaje + interes + iva)
		respuesta.append({"estatus":"1","almacenaje":almacenaje,"interes":interes,"iva":iva,"refrendo":refrendo})
		
		return respuesta


	#funcion para calcular el refrendo, en base al nuevo mutuo
	#se usa para la simulacion
	#para calcular el mutuo actual, revisar la funcion fn_calcula_refrendo
	def fn_simula_calcula_refrendo(self,mutuo):
		p_almacenaje = decimal.Decimal(self.almacenaje)/decimal.Decimal(100)
		p_interes = decimal.Decimal(self.interes)/decimal.Decimal(100)
		p_iva = decimal.Decimal(self.iva)/decimal.Decimal(100)

		almacenaje = 0.00
		interes = 0.00
		iva=0.00
		refrendo = 0.00

		respuesta = []

		almacenaje = (decimal.Decimal(mutuo) * p_almacenaje)
		interes = (decimal.Decimal(mutuo) * p_interes)
		iva = ((almacenaje+interes) * p_iva)
		refrendo = round(almacenaje + interes + iva)
		respuesta.append({"estatus":"1","almacenaje":almacenaje,"interes":interes,"iva":iva,"refrendo":refrendo})		
		return respuesta

	def fn_simula_calcula_refrendo_2(mutuo,sucursal,id_tipo_producto):

		#cie = Configuracion_Interes_Empeno.objects.get(sucursal = sucursal)

		if id_tipo_producto == 1:
			p_almacenaje = decimal.Decimal(sucursal.fn_get_almacenaje(1))/decimal.Decimal(100)
			p_interes = decimal.Decimal(sucursal.fn_get_interes(1))/decimal.Decimal(100)
			p_iva = decimal.Decimal(sucursal.fn_get_iva(1))/decimal.Decimal(100)
		if id_tipo_producto == 2:
			p_almacenaje = decimal.Decimal(sucursal.fn_get_almacenaje(2))/decimal.Decimal(100)
			p_interes = decimal.Decimal(sucursal.fn_get_interes(2))/decimal.Decimal(100)
			p_iva = decimal.Decimal(sucursal.fn_get_iva(3))/decimal.Decimal(100)

		if id_tipo_producto == 3:
			p_almacenaje = decimal.Decimal(sucursal.fn_get_almacenaje(3))/decimal.Decimal(100)
			p_interes = decimal.Decimal(sucursal.fn_get_interes(3))/decimal.Decimal(100)
			p_iva = decimal.Decimal(sucursal.fn_get_iva(3))/decimal.Decimal(100)


		almacenaje = 0.00
		interes = 0.00
		iva=0.00
		refrendo = 0.00

		respuesta = []

		almacenaje = (decimal.Decimal(mutuo) * p_almacenaje)
		interes = (decimal.Decimal(mutuo) * p_interes)
		iva = ((almacenaje+interes) * p_iva)
		refrendo = round(almacenaje + interes + iva)
		respuesta.append({"estatus":"1","almacenaje":almacenaje,"interes":interes,"iva":iva,"refrendo":refrendo})		
		return respuesta

	def fn_get_numero_abonos(self):
		numero_abonos = Abono.objects.filter(boleta = self).count()
		return int(numero_abonos)


	#funcion que regresa un diccionario con los valores "min_semanas" y "max_semanas"
	# el min de semanas es el mino de semanas a refrendar por la boleta
	# el max de semanas es el maximo de semanas a regrendar permitidas por la boleta.
	# aplica solo para boletas semanales.
	def fn_get_min_y_max_semanas_a_pagar(self):
		
		max_semanas_a_refrendar = 0
		min_semanas_a_refrendar = 0

		#consultamos el numero de pagos que estan vencidos y sin pagar de la boleta, excluyendo las comision de periodo de gracia (tipo 2)
		num_pagos_vencidos = Pagos.objects.filter(boleta = self, vencido = 'S',pagado = "N").exclude(tipo_pago__id = 2).count()
		
		#si no tiene pagos vencidos.
		if num_pagos_vencidos == 0:
			#buscamos el proximo pago que no este vencido ni pagado y que sea refrendo o refrendo pg
			id_proximo_pago = Pagos.objects.filter(boleta = self, vencido = "N",pagado = "N").exclude(tipo_pago__id = 2).aggregate(Min("id"))["id__min"]
		
			prox_pago = Pagos.objects.get(id = id_proximo_pago)

			#validamos si el dia actual esta dentro del rango de este pago.
			today = datetime.combine(date.today(),time.min)


			dif_dias = abs((today - prox_pago.fecha_vencimiento_real).days)


			#Si la diferencia entre hoy y la fecha de vencimiento real, es mayor a 6, quiere decir que el dia de
			#hoy aun es parte de alguna semana de pago.
			if dif_dias > 6 :
				
				if dif_dias == 7:#si es 7
					#si es el dia en que se genero la boleta se cobra

					if datetime.combine(self.fecha,time.min) == today :
						max_semanas_a_refrendar = 1
						min_semanas_a_refrendar = 1
					else:
						max_semanas_a_refrendar = 0
						min_semanas_a_refrendar = 0
				else:
					max_semanas_a_refrendar = 0
					min_semanas_a_refrendar = 0
				#if prox_pago.pagado == "N":
				#	max_semanas_a_refrendar = 1
				#	min_semanas_a_refrendar = 1
				#else:
				#	max_semanas_a_refrendar = 0
				#	min_semanas_a_refrendar = 0
			#si la diferencia entre hoy y la fecha de vencimiento real, es menor o igual a 7, quiere edcir que el dia de 
			#hoy si pertenece a una semana de pago
			else:
				if prox_pago.pagado == "S":
					max_semanas_a_refrendar = 0
					min_semanas_a_refrendar = 0
				else:
					max_semanas_a_refrendar = 1
					min_semanas_a_refrendar = 1

		elif num_pagos_vencidos > 0 and num_pagos_vencidos <= 4:
			min_semanas_a_refrendar = 1
			max_semanas_a_refrendar = num_pagos_vencidos + 1
		else:
			min_semanas_a_refrendar = num_pagos_vencidos - 3
			max_semanas_a_refrendar = num_pagos_vencidos + 1

		return {"max_semanas_a_refrendar":max_semanas_a_refrendar,"min_semanas_a_refrendar":min_semanas_a_refrendar}

	#funcion que regresa true en caso de que la boleta acepte refrendo (es porque esta en estatus 1-abierta, 3-almoneda o 5-remate)
	#o false si no acepta refrendo.
	def fn_acepta_refrendo(self):
		if self.estatus.id == 1 or self.estatus.id == 3 or self.estatus.id == 5:
			return True
		else:
			return False

	def fn_get_comision_pg(self):		
		#sumamos todas las comisiones de periodos de gracia que no han sido pagados
		importe_cpg = Pagos.objects.filter(boleta = self,pagado = "N", tipo_pago__id = 2).aggregate(Sum("importe"))["importe__sum"]
		if importe_cpg == None:
			importe_cpg = 0
		return importe_cpg

	def fn_get_dias_vencida(self):
		#si es estatus almoneda o remate, regresamos el tiempo que lleva vencida la boleta.
		if self.estatus.id == 3 or self.estatus.id == 5:
			today = datetime.combine(date.today(),time.max)
			dias_vencido = (today-self.fecha_vencimiento).days

			#no deberia pasar que sea negativo, pero por si acaso
			if dias_vencido < 0:
				dias_vencido = 0

			return dias_vencido
		else:
			return 0 

	#este para plazo semanal
	def fn_simula_proximos_pagos(self,semanas_a_refrendar):
		min_semanas = self.fn_get_min_y_max_semanas_a_pagar()["min_semanas_a_refrendar"]
		max_semanas = self.fn_get_min_y_max_semanas_a_pagar()["max_semanas_a_refrendar"]

		#si el numero de semanas esta fuera de rango
		if semanas_a_refrendar < min_semanas or semanas_a_refrendar > max_semanas:
			return None

		#despues de aplicar un refrendo, deben quedar siempre 4 pagos sin pagar, sin importar si estan vencidos o no.

		#si la boleta esta vencida
		if self.estatus.id ==3 or self.estatus.id ==5:					
			pagos_que_continuan = Pagos.objects.filter(boleta = self, pagado = "N").exclude(tipo_pago__id = "2").order_by("id")[semanas_a_refrendar:max_semanas]
			#Solo puede haber 4 pagos maximos sin pagar despues de aplicar el refrendo,			
			num_nuevos_pagos = 4 - pagos_que_continuan.count()
		else:
			#en toda boleta no venvida, debera haber 4 semanas sin pagar.
			pagos_que_continuan = Pagos.objects.filter(boleta = self, pagado = "N").exclude(tipo_pago__id = "2").order_by("id")[semanas_a_refrendar:]
			#por cada semana a refrendar vamos a generar un nuevo pago.
			num_nuevos_pagos = semanas_a_refrendar
		#creamos una lista para almacenar los nuevos pagos
		nuevos_pagos = []
		ultima_fecha_vencimiento = None
		#se agregan los pagos que continuan a la lista de nuevos pagos
		#aunq estos ya estan vencidos, se mostraran en pantalla de simulacion de proximos pagos
		for p in pagos_que_continuan:				
			ultima_fecha_vencimiento = p.fecha_vencimiento						
			nuevos_pagos.append(p.fecha_vencimiento.strftime('%Y-%m-%d'))
		if ultima_fecha_vencimiento == None:
			id_ultimo_abono = Pagos.objects.filter(boleta = self, pagado = "N").exclude(tipo_pago__id = "2").aggregate(Max("id"))["id__max"]
			ultima_fecha_vencimiento = Pagos.objects.get(id=id_ultimo_abono).fecha_vencimiento

		seven_days = timedelta(days = 7)
		fecha_real = ultima_fecha_vencimiento

		for n in range(0,num_nuevos_pagos):			
			
			fecha_real = datetime.combine((fecha_real+seven_days),time.min)				
			ultima_fecha_vencimiento = fecha_real
			ultima_fecha_vencimiento = fn_fecha_vencimiento_valida(ultima_fecha_vencimiento)
			nuevos_pagos.append(ultima_fecha_vencimiento.strftime('%Y-%m-%d'))
			
		return nuevos_pagos

	#si regresa false es que algo fallo, y no debemos continuar con la aplicacion del refrendo.
	@transaction.atomic
	def fn_paga_comision_pg(self,descuento,abono):
		resp = []
		hoy = date.today()
		hoy = datetime.combine(hoy,time.min)

		#si el estatus es diferente de almoneda o remate y se va a aplicar un decuento es que algo salio mal.
		#ya que no es posible aplicar descuento a una boleta que no esta en almoneda o en remate.
		if self.estatus.id != 3 and self.estatus.id != 5:
			if int(descuento) > 0:				
				resp.append(False)
				resp.append("No es posible aplicar descuento a la boleta.")
				return resp
			else:
				resp.append(True)
				return resp

		#SI ESTAMOS EN ESTE PUNTO ES QUE LA BOLETA SI ESTA EN ALMONEDA O REMATE.
		#obtenemos todos las comisiones de Pg que no han sido pagadoas.
		comision_pg = Pagos.objects.filter(boleta = self,tipo_pago__id = 2,pagado = "N")

		#en caso de quela boleta tenga inconsistencias entre el numero de dias vencidos y el nuero de comisiones pg no pagadas.
		#if self.fn_get_dias_vencida() != comision_pg.count():
		#	resp.append(False)
		#	resp.append("La boleta presenta inconcistencias entre los dias vencidos y el importe de comisiones pg.")
		#	return resp

		pagos_no_pagados = Pagos.objects.filter(boleta = self,pagado = "N")
		importe_comision_pg = comision_pg.aggregate(Sum("importe"))["importe__sum"]

		if importe_comision_pg == None:
			importe_comision_pg = 0		

		if float(descuento) > 0:
			#para aplicar descuento debe tener mas de 0 y 3 o menos dias vencidos			
			if comision_pg.count() > 3:				
				resp.append(False)
				resp.append("No es posible aplicar descuento a la boleta. Tiene más de tres dias vencida.")
				
				return resp

			#validamos que el descuento cubra todas las comisiones de periodo de gracia.
			if float(descuento) < float(importe_comision_pg):				
				resp.append(False)
				resp.append("El importe de descuento no cubre las comisiones de periodo de gracia.")
				return resp



		if comision_pg.exists():			

			
			if descuento == 0:					
				try:
					for cpg in comision_pg:
						cpg.pagado = "S"
						cpg.fecha_pago=timezone.now()
						cpg.save()								

						#creamos la relacion entre el abono y los pagos
						rel=Rel_Abono_Pago()
						rel.abono=abono
						rel.pago=cpg
						rel.save()
				except Exception as e:	
					resp.append(False)				
					return resp

			else:				
				#al aplicar descuento, no se cobran las comisiones pg,
				#por lo tanto se eliminan, pero en cas de querer cancelar el refrendo
				#se almacenan en la tabla tempora Pagos_Com_Pg_No_Usados por un dia
				#osea que un refrendo solo se puede cancelar el mismo dia en que se aplico.				
				try:
					for cpg in comision_pg:
						resp_com_pg = Pagos_Com_Pg_No_Usados()
						resp_com_pg.tipo_pago = cpg.tipo_pago
						resp_com_pg.boleta = cpg.boleta
						resp_com_pg.fecha_vencimiento = cpg.fecha_vencimiento
						resp_com_pg.almacenaje = cpg.almacenaje
						resp_com_pg.interes = cpg.interes
						resp_com_pg.iva = cpg.iva
						resp_com_pg.importe = cpg.importe
						resp_com_pg.vencido = cpg.vencido
						resp_com_pg.pagado = cpg.pagado
						resp_com_pg.fecha_pago = cpg.fecha_pago
						resp_com_pg.fecha_vencimiento_real = cpg.fecha_vencimiento_real
						resp_com_pg.abono = abono
						resp_com_pg.save()
					comision_pg.delete()															
				except Exception as e:							
					resp.append(False)				
					return resp

		resp.append(True)				
		return resp

	#el importe a pagos que aqui se recibe es el importe despues de haber descontado 
	#el importe a comision de PG (en caso de que los tenga.)
	@transaction.atomic
	def fn_salda_pagos(self,numero_semanas_a_pagar,importe_a_pagos,abono):

		resp = []

		#el importe a pagos debe ser mayor o igual a el importe que corresponde al numero de semanas a pagar
		comision_pg = Pagos.objects.filter(boleta = self, pagado = "N",tipo_pago__id = 2)
		#si existe comision Pg, es que algo salio mal, y no debemos continuar
		if comision_pg.exists():
			resp.append(False)
			resp.append("Error al pagar las semanas indicadas. No se liquidaron correctamente las comisiones de periodo de gracia.")
			return resp

		#validamos que la boleta tenga la fecha de vencimiento y fecha de vencimiento real correctas
		if (self.fecha_vencimiento-self.fecha_vencimiento_real).days !=0 and (self.fecha_vencimiento-self.fecha_vencimiento_real).days !=1:
			resp.append(False)
			resp.append("Error al pagar las semanas indicadas. La fecha de vencimiento de la boleta es diferente a la fecha de vencimiento real.")
			return resp


		#buscamos los pagos que se van a saldar
		pagos = Pagos.objects.filter(boleta = self,pagado = "N").exclude(tipo_pago__id = 2)
		#validamos que los pagos tengan la fecha de vencimiento real correcta
		for p in pagos:
			if (p.fecha_vencimiento - p.fecha_vencimiento_real).days != 0 and (p.fecha_vencimiento - p.fecha_vencimiento_real).days != 1:
				resp.append(False)
				resp.append("Error al pagar las semanas indicadas. La fecha de vencimiento es diferente a la fecha de vencimiento real.")
				return resp

		#validamos que las semanas a pagar sean correctas
		sem_max_min = self.fn_get_min_y_max_semanas_a_pagar()

		if sem_max_min['max_semanas_a_refrendar'] == 0:
			resp.append(False)
			resp.append("Error al pagar las semanas indicadas. El numero maximo de semanas a pagar es cero.")
			return resp

		if numero_semanas_a_pagar > sem_max_min['max_semanas_a_refrendar'] or numero_semanas_a_pagar < sem_max_min['min_semanas_a_refrendar']:
			resp.append(False)
			resp.append("Error al pagar las semanas indicadas. El numero de semanas a pagar no es correcto.")
			return resp

		#sin contar los pagos por comision pg
		importe_semanal = Pagos.objects.filter(boleta = self, pagado = "N").exclude(tipo_pago__id = 2).aggregate(Max("importe"))["importe__max"]

		#si no encuentra el importe semanal es porque algo fallo.
		if importe_semanal == None:			
			resp.append(False)
			resp.append("Error al pagar las semanas indicadas.")
			return resp
			

		importe_pagos = int(importe_semanal) * numero_semanas_a_pagar

		#validamos que el importe a pagos (ya descontamos el importe de comision pg)
		#cubra al 100% el importe a pagos.
		#de lo contrario regresa false.
		if importe_a_pagos < importe_pagos:		
			resp.append(False)
			resp.append("Error al pagar las semanas indicadas. El importe destinado a refrendos no cubre el numero de semanas indicadas.")
			return resp

		#si paso las validaciones anteriores, aplicamos el abono.

		fecha_vencimiento_aux = self.fecha_vencimiento 
		fecha_vencimiento_real_aux = self.fecha_vencimiento_real 

		#obtenemos los proximos pagos.
		nuevos_pagos = self.fn_simula_proximos_pagos(numero_semanas_a_pagar)


		#buscamos los pagos a los que afectara.
		pagos = Pagos.objects.filter(boleta = self,pagado = "N").exclude(tipo_pago__id = 2).order_by("id")[:numero_semanas_a_pagar]

		#se obtiene la ultima fecha de vencimiento real de refrendo o refrendo pg
		#ya que desde ahi se empieza a contar la fecha de vencimiento real de  los nuevos pagos			
		fecha_vencimiento_real = Pagos.objects.filter(boleta = self,pagado = "N").exclude(tipo_pago__id = 2).aggregate(Max("fecha_vencimiento_real"))["fecha_vencimiento_real__max"]

		try:
			for p in pagos:
				p.pagado = "S"
				p.tipo_pago = Tipo_Pago.objects.get(id = 1)#cambiamos el pago a refrendo (esto porque de lo contrario fallaria en el job de pagos vencidos.)
				p.fecha_pago = timezone.now()
				p.save()

				#creamos la relacion entre el abono y los pagos
				rel=Rel_Abono_Pago()
				rel.abono=abono
				rel.pago=p
				rel.save()

			tp_refrendo = Tipo_Pago.objects.get(id = 1)

			resp_cr = self.fn_calcula_refrendo()
			
			almacenaje=decimal.Decimal(resp_cr[0]["almacenaje"])/decimal.Decimal(4.00)
			interes=decimal.Decimal(resp_cr[0]["interes"])/decimal.Decimal(4.00)
			iva=decimal.Decimal(resp_cr[0]["iva"])/decimal.Decimal(4.00)
			refrendo=round(decimal.Decimal(resp_cr[0]["refrendo"])/decimal.Decimal(4.00))

			#creamos los nuevos pagos.
			for np in nuevos_pagos:	
				pago = Pagos.objects.filter(boleta = self,pagado = "N",fecha_vencimiento = datetime.strptime(np,'%Y-%m-%d')).exclude(tipo_pago__id = 2)
				
				
				if not pago.exists():
					#la fecha de vencimiento real se incrementa de a 7 dias.
					fecha_vencimiento_real = fecha_vencimiento_real + timedelta(days = 7)
					pgo=Pagos()					
					pgo.tipo_pago=tp_refrendo
					pgo.boleta=self
					pgo.fecha_vencimiento = datetime.strptime(np,'%Y-%m-%d')
					pgo.almacenaje=almacenaje
					pgo.interes=interes
					pgo.iva=iva
					pgo.importe=refrendo
					pgo.vencido="N"
					pgo.pagado="N"
					pgo.fecha_vencimiento_real = fecha_vencimiento_real#datetime.strptime(np,'%Y-%m-%d')

					#en caso de cancelar el refrendo, necesitamos saber que semanas genero el refrendo.
					#para poder eliminarlas.
					pgo.abono = abono
					pgo.save()
				else:
					for p in pago:
						p.tipo_pago = tp_refrendo
						p.save()

				self.fecha_vencimiento = datetime.strptime(np,'%Y-%m-%d')
				self.fecha_vencimiento_real = fecha_vencimiento_real

			estatus_abierta = Estatus_Boleta.objects.get(id = 1)
			
			self.estatus = estatus_abierta
			self.save()

			#despues de haber aplicado el abono, validamos que la boleta este correcta.
			#validamos las fechas de vencimiento y vencimiento real de la boleta
			if (self.fecha_vencimiento-self.fecha_vencimiento_real).days !=0 and (self.fecha_vencimiento-self.fecha_vencimiento_real).days != 1:
				resp.append(False)
				resp.append("Error al pagar las semanas indicadas. No se pudo calcular la fecha de vencimiento de la boleta.")
				return resp

			pagos = Pagos.objects.filter(boleta = self,pagado = "N")

			for p in pagos:
				if (p.fecha_vencimiento - p.fecha_vencimiento_real).days != 0 and (p.fecha_vencimiento - p.fecha_vencimiento_real).days != 1:
					resp.append(False)
					resp.append("Error al pagar las semanas indicadas. No se pudo calcular la fecha de vencimiento de los proximos pagos.")
					return resp										


			resp.append(True)
			
			return resp
		except Exception as e:
			print(str(e))
			resp.append(False)
			resp.append("Error al pagar las semanas indicadas.")
			return resp

	@transaction.atomic
	def fn_abona_capital(self,importe_capital,abono):
		try:

			print("empezamos el abono a capital")
			#validamos que la boleta tenga como maximo numero de pagos 0
			#ya que de lo contrario, no puede abonar a capital.
			max_semanas_a_refrendar = self.fn_get_min_y_max_semanas_a_pagar()["max_semanas_a_refrendar"]
			
			if max_semanas_a_refrendar != 0:
				return False

			if type(importe_capital) != type(0):
				return False

			mutuo=self.mutuo
			mutuo=int(mutuo)-int(importe_capital)

			#actualizamos el mutuo del la boleta.
			self.mutuo=mutuo
			self.save()

			rel_cap = Rel_Abono_Capital()
			rel_cap.boleta = self
			rel_cap.abono = abono
			rel_cap.importe = importe_capital
			rel_cap.capital_restante = mutuo
			rel_cap.save()

			resp=self.fn_calcula_refrendo()

			almacenaje=decimal.Decimal(resp[0]["almacenaje"])/decimal.Decimal(4.00)
			interes=decimal.Decimal(resp[0]["interes"])/decimal.Decimal(4.00)
			iva=decimal.Decimal(resp[0]["iva"])/decimal.Decimal(4.00)
			refrendo=round(decimal.Decimal(resp[0]["refrendo"])/decimal.Decimal(4.00))		

			est_refrendo = Tipo_Pago.objects.get(id = 1)
			#buscamos los abonos no pagados y no vencidos para actualizar su importe en base al nuevo mutuo
			pagos_t=Pagos.objects.filter(pagado="N",tipo_pago=est_refrendo,boleta=self,vencido="N").order_by("id")


			#actualizamos el importe de los pagos con el nuevo refrendo.
			for pt in pagos_t:
				if mutuo!=0:
					pt.importe=refrendo
					pt.almacenaje=almacenaje
					pt.interes=interes
					pt.iva=iva
					pt.save()
				else:					
					#respaldamos los pagos no usados (por el desempeño) para en caso de cancelar el abono podramos restaurarlo.
					resp_pagos = Pagos_No_Usados()
					resp_pagos.tipo_pago = pt.tipo_pago
					resp_pagos.boleta = pt.boleta
					resp_pagos.fecha_vencimiento = pt.fecha_vencimiento
					resp_pagos.almacenaje = pt.almacenaje
					resp_pagos.interes = pt.interes
					resp_pagos.iva = pt.iva
					resp_pagos.importe = pt.importe
					resp_pagos.vencido = pt.vencido
					resp_pagos.pagado = pt.pagado
					resp_pagos.fecha_pago = pt.fecha_pago
					resp_pagos.fecha_vencimiento_real = pt.fecha_vencimiento_real
					resp_pagos.abono = pt.abono#el abono que genero el refrendo
					resp_pagos.abono_respaldo = abono
					resp_pagos.save()

					pt.delete()
					#marcamos la boleeta como desempeñada.
					desempenada=Estatus_Boleta.objects.get(id=4)
					self.estatus=desempenada
					self.mutuo=0
					self.refrendo=0
					self.save()
			return True
		except Exception as e:
			print(e)			
			return False


	def fn_calcula_precio_venta(self):
		#si se definio un precio de venta fijo, ese es el que regresa
		if self.precio_venta_fijo != 0:
			return self.precio_venta_fijo

		importe_venta=0.00

		porcentaje = Porcentaje_Sobre_Avaluo.objects.all().aggregate(Sum("porcentaje"))

		porce = 0;
		if porcentaje["porcentaje__sum"]!=None:
			porce = decimal.Decimal(porcentaje["porcentaje__sum"])

		importe_venta = decimal.Decimal(self.avaluo) + (decimal.Decimal(self.avaluo)*(decimal.Decimal(porce)/decimal.Decimal(100.00)))
		return importe_venta

	def fn_calcula_precio_apartado(self):	
		#si se definio un precio de venta fijo, ese es el que regresa
		if self.precio_venta_fijo != 0:
			return self.precio_venta_fijo
			
		importe_venta=0.00
		porcentaje=Porcentaje_Sobre_Avaluo.objects.all().aggregate(Sum("porcentaje_apartado"))
		porce=0;

		if porcentaje["porcentaje_apartado__sum"]!=None:
			porce=decimal.Decimal(porcentaje["porcentaje_apartado__sum"])

			importe_venta=decimal.Decimal(self.avaluo)+(decimal.Decimal(self.avaluo)*(decimal.Decimal(porce)/decimal.Decimal(100.00)))

		return importe_venta
	def fn_establece_precio_venta_y_apartado(self,importe,id_usuario):
		resp = []
		try:
			self.precio_venta_fijo = importe
			self.usuario_establece_precio_fijo = User.objects.get(id = id_usuario)
			self.save()
			resp.append(True)			
		except Exception as e:
			print("fn_establece_precio_venta_y_apartado:- " + str(e))
			resp.append(False)			
		return resp


	class Meta:
		unique_together=("folio",'sucursal',)




class Venta_Temporal_Piso(models.Model):
	usuario=models.ForeignKey(User,on_delete=models.PROTECT,null=True,blank=True)
	boleta=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT)

	class Meta:
		unique_together=("usuario","boleta")

class Apartado_Temporal(models.Model):
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
	boleta=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT)

	class Meta:
		unique_together=("usuario","boleta")

class Estatus_Apartado(models.Model):
	estatus=models.CharField(max_length=20,null=False)

	def __str__(self):
		return self.estatus

class Apartado(models.Model):
	folio=models.CharField(max_length=7,null=True)
	usuario=models.ForeignKey(User,on_delete=models.PROTECT,null=True,blank=True,related_name="usuario_apartado")#el usuario que realiza la venta en el sistema
	fecha=models.DateTimeField(default=timezone.now)		
	importe_venta=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)#es elimporte real de la venta, en cuanto realmente se vendio el producto
	caja=models.ForeignKey(Cajas,on_delete=models.PROTECT,blank=True,null=True)#es la caja que se tenia aberta cuando se ingreso el dinero.
	cliente=models.ForeignKey(Cliente,on_delete=models.PROTECT,blank=True,null=True)
	saldo_restante=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)#es el importe que falta para terminar de pagar la prenda.
	estatus=models.ForeignKey(Estatus_Apartado,on_delete=models.PROTECT,null=True,blank=True)
	boleta=models.OneToOneField(Boleta_Empeno,on_delete=models.PROTECT,null=True,blank=True)#como solo una boleta puede estar apartada a la vez, no necesitamos el detalle.
	fecha_vencimiento=models.DateTimeField(null=True,blank=True)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT,blank=True,null=True)	
	nombre_cliente = models.CharField(max_length = 100,default = '')
	telefono = models.CharField(max_length = 10,default = '')

class Abono_Apartado(models.Model):
	folio=models.CharField(max_length=7,null=True)
	usuario=models.ForeignKey(User,on_delete=models.PROTECT,null=True,blank=True,related_name="usuario_ab_apartado")
	fecha=models.DateTimeField(default=timezone.now)		
	importe=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	caja=models.ForeignKey(Cajas,on_delete=models.PROTECT,blank=True,null=True)#es la caja que se tenia aberta cuando se ingreso el dinero.
	apartado=models.ForeignKey(Apartado,on_delete=models.PROTECT)


class Imprime_Apartado(models.Model):
	usuario=models.OneToOneField(User,on_delete=models.PROTECT,null=True,blank=True)
	apartado=models.ForeignKey(Apartado,on_delete=models.PROTECT)
	abono=models.OneToOneField(Abono_Apartado,on_delete=models.PROTECT,null=True,blank=True)


class Venta_Piso(models.Model):
	folio=models.CharField(max_length=7,null=True)
	usuario=models.ForeignKey(User,on_delete=models.PROTECT,null=True,blank=True,related_name="usuario")#el usuario que realiza la venta en el sistema
	fecha=models.DateTimeField(default=timezone.now)	
	importe_mutuo=models.DecimalField(max_digits=20,decimal_places=2)
	importe_avaluo=models.DecimalField(max_digits=20,decimal_places=2)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)	
	importe_venta=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)#es elimporte real de la venta, en cuanto realmente se vendio el granel
	caja=models.ForeignKey(Cajas,on_delete=models.PROTECT,blank=True,null=True)#es la caja que se tenia aberta cuando se ingreso el dinero.
	cliente=models.ForeignKey(Cliente,on_delete=models.PROTECT,blank=True,null=True)
	nombre_cliente = models.CharField(max_length = 100,default = '')
	telefono = models.CharField(max_length = 10,default = '')


class Det_Venta_Piso(models.Model):
	venta=models.ForeignKey(Venta_Piso,on_delete=models.PROTECT)
	boleta=models.OneToOneField(Boleta_Empeno,on_delete=models.PROTECT)
	importe_venta=models.IntegerField(default=0)

class Imprime_Venta_Piso(models.Model):
	usuario=models.OneToOneField(User,on_delete=models.PROTECT,null=True,blank=True)
	venta_piso=models.ForeignKey(Venta_Piso,on_delete=models.PROTECT)



class Venta_Temporal(models.Model):
	usuario=models.ForeignKey(User,on_delete=models.PROTECT,null=True,blank=True)
	boleta=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT,null=True,blank=True)
	fecha=models.DateTimeField(null=True,blank=True)#la venta temporal se almacena por un dia, al siguiente dia se elimina.q
	vender=models.CharField(max_length=1,default='N')

	class Meta:
		unique_together=("usuario","boleta")

class Venta_Granel(models.Model):
	usuario=models.ForeignKey(User,on_delete=models.PROTECT,null=True,blank=True,related_name="usuario2")#el usuario que realiza la venta en el sistema
	fecha=models.DateTimeField(default=timezone.now)	
	importe_mutuo=models.DecimalField(max_digits=20,decimal_places=2)
	importe_avaluo=models.DecimalField(max_digits=20,decimal_places=2)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)	
	importe_venta=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)#es elimporte real de la venta, en cuanto realmente se vendio el granel
	usuario_finaliza=models.ForeignKey(User,on_delete=models.PROTECT,null=True,blank=True,related_name="usuario_finaliza")#el usuario que fisicamente realiza la venta y da ingreso al dinero de la venta		
	caja=models.ForeignKey(Cajas,on_delete=models.PROTECT,blank=True,null=True)#es la caja que se tenia aberta cuando se ingreso el dinero.
	fecha_importe_venta=models.DateTimeField(null=True,blank=True)

class Det_Venta_Granel(models.Model):
	venta=models.ForeignKey(Venta_Granel,on_delete=models.PROTECT)
	boleta=models.OneToOneField(Boleta_Empeno,on_delete=models.PROTECT)

class Imprime_Venta_Granel(models.Model):
	usuario=models.OneToOneField(User,on_delete=models.PROTECT,null=True,blank=True)
	venta_granel=models.ForeignKey(Venta_Granel,on_delete=models.PROTECT)


class Det_Boleto_Empeno(models.Model):
	boleta_empeno=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT)
	tipo_producto=models.ForeignKey(Tipo_Producto,on_delete=models.PROTECT)
	linea=models.ForeignKey(Linea,on_delete=models.PROTECT)
	sub_linea=models.ForeignKey(Sub_Linea,on_delete=models.PROTECT)	
	marca=models.ForeignKey(Marca,on_delete=models.PROTECT)
	descripcion=models.CharField(max_length=50,null=False)
	costo_kilataje=models.ForeignKey(Costo_Kilataje,on_delete=models.PROTECT,blank=True,null=True)
	peso=models.DecimalField(max_digits=20,decimal_places=2,default=0.00,null=True,blank=True)
	avaluo=models.IntegerField()
	mutuo_sugerido=models.IntegerField()
	mutuo=models.IntegerField()
	observaciones=models.TextField(null=True,blank=True)

##se llena al generar un empeño
#lo usamos como auxiliar para imprimir las boletas.
class Imprimir_Boletas(models.Model):
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
	boleta=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT)
	reimpresion=models.IntegerField(default=0)#cuando tenga 1 es que es reimpresion y se le cobra 10 pesos.



class Tipo_Pago(models.Model):
	tipo_pago=models.CharField(max_length=30,null=False)

	def __str__(self):
		return self.tipo_pago

class Costo_Extra(models.Model):
	descripcion=models.CharField(max_length=50,null=False)
	costo=models.IntegerField(default=0)

class Reg_Costos_Extra(models.Model):
	costo_extra=models.ForeignKey(Costo_Extra,on_delete=models.PROTECT)
	fecha=models.DateTimeField(default=timezone.now)
	caja=models.ForeignKey(Cajas,on_delete=models.PROTECT)
	boleta=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT)
	importe=models.IntegerField()

class Abono(models.Model):
	folio = models.CharField(max_length=7,null=True)
	tipo_movimiento = models.ForeignKey(Tipo_Movimiento,on_delete=models.PROTECT,null=True,blank=True)
	sucursal = models.ForeignKey(Sucursal,on_delete=models.PROTECT,null=True,blank=True)	
	fecha = models.DateTimeField(default=timezone.now)
	usuario = models.ForeignKey(User,on_delete=models.PROTECT,related_name = "usuario_alta_abono")
	importe = models.DecimalField(max_digits=20,decimal_places=2,default=0.00)	
	caja = models.ForeignKey(Cajas,on_delete=models.PROTECT,blank=True,null=True)
	boleta = models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT,blank=True,null=True)
	estatus = models.CharField(choices = ESTATUS_ABONO,max_length = 10,default = "ACTIVO")
	usuario_cancela = models.ForeignKey(User,on_delete = models.PROTECT,null = True,blank = True,related_name = "usuario_cancela_abono")

	#funcion para cancelar abono
	@transaction.atomic
	def fn_cancela_abono(self,usuario):
		hoy = datetime.combine(date.today(),time.min)
		fecha_abono = datetime.combine(self.fecha,time.min)

		resp = []

		if hoy != fecha_abono:
			resp.append(False)
			resp.append("El abono no puede ser cancelado ya que no es del dia de hoy.")
			return resp

		abonos_posteriores = Abono.objects.filter(boleta = self.boleta, id__gt = self.id)

		if abonos_posteriores.exists():
			resp.append(False)
			resp.append("El abono no puede ser cancelado ya que existe un abono posterior al que intenta cancelar.")
			return resp

		if self.boleta.estatus_anterior == None:
			resp.append(False)
			resp.append("El abono no puede ser cancelado ya que no es posible calcular el estatus de boleta anterior.")
			return resp

		if self.boleta.fecha_vencimiento_anterior == None or self.boleta.fecha_vencimiento_real_anterior == None:
			resp.append(False)
			resp.append("El abono no puede ser cancelado ya que no es posible calcular la fecha de vencimiento anterior.")
			return resp



		#si llegamos a este punto es que el abono si se puede cancelar.

		#eliminamos los pagos que se generaron al aplicar el refrendo
		Pagos.objects.filter(abono = self).delete()
		#regresamos el estatus de la boleta.
		self.boleta.fecha_vencimiento = self.boleta.fecha_vencimiento_anterior
		self.boleta.fecha_vencimiento_real = self.boleta.fecha_vencimiento_real_anterior
		self.boleta.estatus = self.boleta.estatus_anterior
		self.boleta.save()

		#obtenemos las comisiones pg a las que se le aplico descuento con el abono.
		pagos_pg = Pagos_Com_Pg_No_Usados.objects.filter(abono = self)

		if pagos_pg.exists():
			for p in pagos_pg:			
				pago = Pagos()
				pago.tipo_pago = p.tipo_pago
				pago.boleta = p.boleta
				pago.fecha_vencimiento = p.fecha_vencimiento
				pago.almacenaje = p.almacenaje
				pago.interes = p.interes
				pago.iva = p.iva
				pago.importe = p.importe
				pago.vencido = p.vencido
				pago.pagado = "N"
				pago.fecha_pago = None
				pago.fecha_vencimiento_real = p.fecha_vencimiento_real
				pago.save()

			Pagos_Com_Pg_No_Usados.objects.filter(abono = self).delete()

		#obtenemos los pagos no usados en caso de desempeño y los restauramos
		pagos_resp = Pagos_No_Usados.objects.filter(abono_respaldo = self)
		if pagos_resp.exists():
			for p in pagos_resp:			
				pago = Pagos()
				pago.tipo_pago = p.tipo_pago
				pago.boleta = p.boleta
				pago.fecha_vencimiento = p.fecha_vencimiento
				pago.almacenaje = p.almacenaje
				pago.interes = p.interes
				pago.iva = p.iva
				pago.importe = p.importe
				pago.vencido = p.vencido
				pago.pagado = "N"
				pago.fecha_pago = None
				pago.fecha_vencimiento_real = p.fecha_vencimiento_real
				pago.abono = p.abono
				pago.save()

			Pagos_No_Usados.objects.filter(abono = self).delete()

		#eliminamos los pagos que fueron generados por el abono que se esta cancelando.
		Pagos.objects.filter(abono = self).delete()


		#validamos si afecto abono a capital, y lo regresamos.
		if Rel_Abono_Capital.objects.filter(abono = self).exists():			
			self.boleta.mutuo = self.boleta.mutuo + Rel_Abono_Capital.objects.get(abono = self).importe			
			self.boleta.save()
			Rel_Abono_Capital.objects.filter(abono = self).delete()

		#calculamos el refrendo en base al nuevo mutuo
		r = self.boleta.fn_calcula_refrendo()


		almacenaje = decimal.Decimal(r[0]["almacenaje"])/decimal.Decimal(4.00)
		interes = decimal.Decimal(r[0]["interes"])/decimal.Decimal(4.00)
		iva = decimal.Decimal(r[0]["iva"])/decimal.Decimal(4.00)
		refrendo = round(decimal.Decimal(r[0]["refrendo"])/decimal.Decimal(4.00))

		self.boleta.refrendo = math.ceil((refrendo * 4.00))
		self.boleta.save()


		#en cso d que se haya abonado a capital, aplicamos rollback a el importe de refrendo semanal.
		for pago in Pagos.objects.filter(boleta = self.boleta,pagado = "N").exclude(tipo_pago__id = 2):
			pago.almacenaje  = almacenaje
			pago.interes = interes
			pago.iva = iva
			pago.importe = refrendo
			pago.save()

		#obtenemos los pagos (afecta a comisionpg, refrendo y refrendo pg) que afecto el abono y los regresamos a no pagados
		rap = Rel_Abono_Pago.objects.filter(abono = self)		

		
		for p in rap:
			pago = p.pago
			pago.pagado = "N"
			pago.fecha_pago = None		
			pago.save()

		Rel_Abono_Pago.objects.filter(abono = self).delete()

		#los pagos que tengan fecha de vencimiento mayor a la fech de vencimiento de la boleta
		#son considerados Refrendo pg
		for p in Pagos.objects.filter(boleta = self.boleta,pagado = "N").exclude(tipo_pago__id = 2):
			if p.fecha_vencimiento > self.boleta.fecha_vencimiento:
				
				p.tipo_pago = Tipo_Pago.objects.get(id=3)
				p.save()

		self.estatus = "CANCELADO"
		self.usuario_cancela = usuario
		self.importe = 0

		self.save()

		return resp

class Pagos(models.Model):
	tipo_pago=models.ForeignKey(Tipo_Pago,on_delete=models.PROTECT,null=False,blank=True)
	boleta=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT,null=False,blank=True)
	fecha_vencimiento=models.DateTimeField(null=False)
	almacenaje=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	interes=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	iva=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	importe=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	vencido=models.CharField(max_length=1,default='N')
	pagado=models.CharField(max_length=1,default='N',null=False)
	fecha_pago=models.DateTimeField(null=True,blank=True)
	fecha_vencimiento_real=models.DateTimeField(null=True,blank=True)#cuando la fecha de vencimiento cai en dia de asueto, la fecha de vencimienot se recorre un dia, esta fecha nos indica cual es la fecha de vencimiento real para calcular el las futuras fechas de vencimiento.
	abono = models.ForeignKey(Abono,on_delete = models.PROTECT,null = True,blank = True)#Nos indica cual abono lo genero, para en caso de cancelar el abono, debemos eliminar el pago.





class Tipo_Periodo(models.Model):
	tipo_periodo=models.CharField(max_length=20,null=False)

	def __str__(self):
		return self.tipo_periodo

class Periodo(models.Model):
	consecutivo=models.IntegerField(default=0)
	boleta=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT,null=False,blank=True)
	fecha_vencimiento=models.DateTimeField(null=False)
	importe=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	tipo_periodo=models.ForeignKey(Tipo_Periodo,on_delete=models.PROTECT,null=False)
	pago=models.ForeignKey(Pagos,on_delete=models.PROTECT,null=True,blank=True)
	fecha_pago=models.DateTimeField(null=True,blank=True)
	vencido=models.CharField(max_length=1,default='N')
	pagado=models.CharField(max_length=1,default='N',null=False)

#tabla usada para la simulacion de pagos mensual.
class Periodo_Temp(models.Model):
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
	consecutivo=models.IntegerField(default=0)
	boleta=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT,null=False,blank=True)
	fecha_vencimiento=models.DateTimeField(null=False)
	importe=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	tipo_periodo=models.ForeignKey(Tipo_Periodo,on_delete=models.PROTECT,null=False)
	pago=models.ForeignKey(Pagos,on_delete=models.PROTECT,null=True,blank=True)
	fecha_pago=models.DateTimeField(null=True,blank=True)
	vencido=models.CharField(max_length=1,default='N')
	pagado=models.CharField(max_length=1,default='N',null=False)
	
#tabla usada para la simulacion de pagos semanal
class Pagos_Temp(models.Model):
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
	tipo_pago=models.ForeignKey(Tipo_Pago,on_delete=models.PROTECT,null=False,blank=True)
	boleta=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT,null=False,blank=True)
	fecha_vencimiento=models.DateTimeField(null=False)
	almacenaje=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	interes=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	iva=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	importe=models.IntegerField()
	vencido=models.CharField(max_length=1,default='N')
	pagado=models.CharField(max_length=1,default='N',null=False)
	fecha_pago=models.DateTimeField(null=True,blank=True)
	fecha_vencimiento_real=models.DateTimeField(null=True,blank=True)

#esta tabla debera llenarse cada inicio de año para marcar los dias no habiles del año y que la fecha de vencimiento no caiga en estos dias.
class Dia_No_Laboral(models.Model):
    fecha=models.DateTimeField()
    
    class Meta:
        unique_together=("fecha",)



#cuando se aplica un refrendo y se le descuento los periodos PG
#se almacenan en esta tabla durante el dia, esto con la finalidad de poder cancelar
#el refrendo en caso de querer. asi podemos regresar los abonos pg.
# por la noche deberan borrarse.
class Pagos_Com_Pg_No_Usados(models.Model):
	tipo_pago=models.ForeignKey(Tipo_Pago,on_delete=models.PROTECT,null=False,blank=True)
	boleta=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT,null=False,blank=True)
	fecha_vencimiento=models.DateTimeField(null=False)
	almacenaje=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	interes=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	iva=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	importe=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	vencido=models.CharField(max_length=1,default='N')
	pagado=models.CharField(max_length=1,default='N',null=False)
	fecha_pago=models.DateTimeField(null=True,blank=True)
	fecha_vencimiento_real=models.DateTimeField(null=True,blank=True)#cuando la fecha de vencimiento cai en dia de asueto, la fecha de vencimienot se recorre un dia, esta fecha nos indica cual es la fecha de vencimiento real para calcular el las futuras fechas de vencimiento.
	abono = models.ForeignKey(Abono,on_delete = models.PROTECT)

#cuando se aplica un refrendo, y este genera un desemepeño, los pagos que no se usaron se eliminan,
#pero en caso  de querer cancelar el abono, vamos a necesitar recuperarlos
#en esta tabla se almacenan para poder restaurarlos.
class Pagos_No_Usados(models.Model):
	tipo_pago=models.ForeignKey(Tipo_Pago,on_delete=models.PROTECT,null=False,blank=True)
	boleta=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT,null=False,blank=True)
	fecha_vencimiento=models.DateTimeField(null=False)
	almacenaje=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	interes=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	iva=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	importe=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	vencido=models.CharField(max_length=1,default='N')
	pagado=models.CharField(max_length=1,default='N',null=False)
	fecha_pago=models.DateTimeField(null=True,blank=True)
	fecha_vencimiento_real=models.DateTimeField(null=True,blank=True)#cuando la fecha de vencimiento cai en dia de asueto, la fecha de vencimienot se recorre un dia, esta fecha nos indica cual es la fecha de vencimiento real para calcular el las futuras fechas de vencimiento.
	abono = models.ForeignKey(Abono,on_delete = models.PROTECT,related_name = "abono_genero",null = True, blank = True )#nos indica el abono que lo genero
	abono_respaldo = models.ForeignKey(Abono,on_delete = models.PROTECT,related_name = "abono_respaldo",null = True,blank = True)#el abono que genero el respaldo

class Imprime_Abono(models.Model):
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
	abono=models.ForeignKey(Abono,on_delete=models.PROTECT)
	reimpresion=models.IntegerField(default=0)

#no manejamos importe ya que un pago tiene que ser cubierto totalmente, no parcialmente.
#aplica solo para pago semanal
class Rel_Abono_Pago(models.Model):
	abono=models.ForeignKey(Abono,on_delete=models.PROTECT)
	pago=models.ForeignKey(Pagos,on_delete=models.PROTECT)

class Rel_Abono_Periodo(models.Model):
	abono=models.ForeignKey(Abono,on_delete=models.PROTECT)
	periodo=models.ForeignKey(Periodo,on_delete=models.PROTECT)	

#cuando un abono afecta a capital, aqui almacenamos a que boleta le afecto el capital y el importe.
class Rel_Abono_Capital(models.Model):
	abono=models.ForeignKey(Abono,on_delete=models.PROTECT)
	boleta=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT)
	importe=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	capital_restante=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)#cuando se afecte el capital, aqui almacenamos el historial de como quedo al aplicar el abono.

class Configuracion_Interes_Empeno(models.Model):
	sucursal = models.OneToOneField(Sucursal,on_delete = models.PROTECT)
	almacenaje_oro = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0.00)
	interes_oro = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0.00)
	iva_oro = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0.00)
	almacenaje_plata = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0.00)
	interes_plata = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0.00)
	iva_plata = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0.00)
	almacenaje_prod_varios = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0.00)
	interes_prod_varios = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0.00)
	iva_prod_varios = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0.00)
	usuario_modifica = models.ForeignKey(User,on_delete=models.PROTECT)
	fecha_modificacion = models.DateTimeField(default = timezone.now)

	#si no encuentra la condiguracion, regresa false para indicar que no la tiene capturada.
	def fn_get_configuracion_interes_empeno(sucursal):
		try:
			return Configuracion_Interes_Empeno.objects.get(sucursal = sucursal)
		except:
			return False

	def fn_set_configuracion_interes_empeno(sucursal,almacenaje_oro,interes_oro,iva_oro,almacenaje_plata,interes_plata,iva_plata,almacenaje_prod_varios,interes_prod_varios,iva_prod_varios,usuario_modifica):
		try:
			cie = Configuracion_Interes_Empeno.objects.get(sucursal = sucursal)
			
			cie.almacenaje_oro=almacenaje_oro
			cie.save()
		except Exception as e:
			print(e)
			cie = fn_actualiza_porcentaje_mutuo()

		
		try:
			cie.almacenaje_oro = almacenaje_oro
			cie.interes_oro = interes_oro
			cie.iva_oro = iva_oro
			cie.almacenaje_plata = almacenaje_plata
			cie.interes_plata = interes_plata
			cie.iva_plata = iva_plata
			cie.almacenaje_prod_varios = almacenaje_prod_varios
			cie.interes_prod_varios = interes_prod_varios
			cie.iva_prod_varios = iva_prod_varios
			cie.usuario_modifica = usuario_modifica
			cie.fecha_modificacion = date.today()
			cie.save()
			return True
		except:
			return False



class Configuracion_Porcentaje_Mutuo(models.Model):
	sucursal = models.OneToOneField(Sucursal,on_delete=models.PROTECT)
	porcentaje_oro = models.IntegerField()
	porcentaje_plata = models.IntegerField()
	porcentaje_articulos_varios = models.IntegerField()








#valida que la fecha de vencimiento no caiga en algun dia de azueto, 
#en caso de caer en dia de azueto, le asigna el siguiente dia habil.
def fn_fecha_vencimiento_valida(fecha_vencimiento):
	try:
		#si el dia es de azueto, buscamos el siguiente hata encontrar un dia que no sea de azueto.
		dv=Dia_No_Laboral.objects.get(fecha=fecha_vencimiento)

		dia_mas = timedelta(days=1)
		#si la fecha de vencimiento existe en los dias inhabiles, buscamos el siguiente dia para que sea el de vencimiento.
		fecha_vencimiento=datetime.combine(fecha_vencimiento+dia_mas, time.min)

		dv=Dia_No_Laboral.objects.get(fecha=fecha_vencimiento)
		dia_mas = timedelta(days=1)

		#si la fecha de vencimiento existe en los dias inhabiles, buscamos el siguiente dia para que sea el de vencimiento.
		fecha_vencimiento=datetime.combine(fecha_vencimiento+dia_mas, time.min)

		dv=Dia_No_Laboral.objects.get(fecha=fecha_vencimiento)
		dia_mas = timedelta(days=1)

		#si la fecha de vencimiento existe en los dias inhabiles, buscamos el siguiente dia para que sea el de vencimiento.
		fecha_vencimiento=datetime.combine(fecha_vencimiento+dia_mas, time.min)

		dv=Dia_No_Laboral.objects.get(fecha=fecha_vencimiento)
		dia_mas = timedelta(days=1)

		#si la fecha de vencimiento existe en los dias inhabiles, buscamos el siguiente dia para que sea el de vencimiento.
		fecha_vencimiento=datetime.combine(fecha_vencimiento+dia_mas, time.min)

	except Exception as e:
		print(e)
		print("la fecha de vencimiento es valida")
	return  fecha_vencimiento

#almacenamos el estatus de cartera a diario
class Historico_Estatus_Cartera(models.Model):
	sucursal = models.ForeignKey(Sucursal,on_delete = models.PROTECT)
	fecha = models.DateTimeField(default = timezone.now())
	num_boletas_activas = models.IntegerField()
	num_boletas_almoneda = models.IntegerField()
	num_boletas_remate = models.IntegerField()
	importe_mutuo_activas = models.DecimalField(decimal_places = 2,max_digits = 26)
	importe_mutuo_almoneda = models.DecimalField(decimal_places = 2,max_digits = 26)
	importe_mutuo_remate = models.DecimalField(decimal_places = 2,max_digits = 26)
	importe_avaluo_activas = models.DecimalField(decimal_places = 2,max_digits = 26)
	importe_avaluo_almoneda = models.DecimalField(decimal_places = 2,max_digits = 26)
	importe_avaluo_remate = models.DecimalField(decimal_places = 2,max_digits = 26)


	class Meta:
		unique_together = ("sucursal","fecha")



#funcion para generar folio de movimiento
def fn_folios(tipo_movimiento,sucursal):
	try:
		cf=Control_Folios.objects.get(tipo_movimiento=tipo_movimiento,sucursal=sucursal)
		folio=cf.folio+1
		cf.folio=folio
		cf.save()		
	except:
		#si no existe registro, crea uno
		Control_Folios.objects.create(tipo_movimiento=tipo_movimiento,sucursal=sucursal,folio=1)
		cf=Control_Folios.objects.get(tipo_movimiento=tipo_movimiento,sucursal=sucursal)
		folio=cf.folio
	return folio


def fn_str_clave(id):
	if len(str(id))==1:
		return '000000'+str(id)
	if len(str(id))==2:
		return '00000'+str(id)
	if len(str(id))==3:
		return '0000'+str(id)
	if len(str(id))==4:
		return '000'+str(id)
	if len(str(id))==5:
		return '00'+str(id)
	if len(str(id))==6:
		return '0'+str(id)
	if len(str(id))==7:
		return str(id)
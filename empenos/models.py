from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from seguridad.models import Session
from datetime import date, datetime, time,timedelta
import calendar
from django.db.models import Sum
import decimal

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


#al momendo de anunciar un producto para la venta piso, 
#se le aumenta un % sobre el avaluo, ese porcentaje es configurable en esta tabla.
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

class Perfil(models.Model):
	perfil=models.CharField(max_length=30,null=False)

	def __str__(self):
		return str(self.id)+' '+self.perfil

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
	saldo=models.IntegerField(default=0)

	def __str__(self):
		return str(self.id)+' '+self.sucursal

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
		refrendo = (almacenaje+interes+iva)
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
			






class Concepto_Retiro(models.Model):
	concepto = models.CharField(max_length = 40,null = False)
	sucursal = models.ForeignKey(Sucursal,on_delete = models.PROTECT,blank=True,null=True)
	importe_maximo_retiro = models.PositiveIntegerField()	
	fecha_alta = models.DateTimeField(default = timezone.now)
	fecha_modificacion = models.DateTimeField(default = timezone.now)
	usuario_ultima_mod = models.ForeignKey(User,on_delete = models.PROTECT)
	activo = models.CharField(choices=SI_NO,max_length=2,default="SI")
	

	def __str__(self):
		return str(self.id)+' '+self.concepto+' '+str(self.importe_maximo_retiro)

	def fn_nuevo_concepto(id_sucursal,id_usuario,importe,concepto):	
		try:
			if concepto == "":
				return False

			if int(importe) < 0 or int(importe) == 0:
				return False

			sucursal = Sucursal.objects.get(id = int(id_sucursal))
			usuario = User.objects.get(id = int(id_usuario))
			Concepto_Retiro.objects.create(activo = 1, concepto = concepto.upper(),sucursal = sucursal,importe_maximo_retiro = importe,usuario_ultima_mod = usuario)
			return True
		except Exception as e:
			
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
	user=models.ForeignKey(User,on_delete=models.PROTECT)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)
	perfil=models.ForeignKey(Perfil,on_delete=models.PROTECT)
	sesion=models.IntegerField(blank=True,null=True)

	class Meta:
		unique_together=('user',)

	def __str__(self):
		return self.user.username

class Control_Folios(models.Model):
	folio=models.IntegerField(null=False)
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento,on_delete=models.PROTECT)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)


class Cajas(models.Model):
	folio=models.CharField(max_length=7,null=True)
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento,on_delete=models.PROTECT)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)
	fecha=models.DateTimeField(default=timezone.now)
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)#usuario que abrio caja.
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
	estatus_guardado=models.IntegerField(default=0)#cuando esta cero es que nunca se ha guardado informacion de cierre de caja, por lo tanto 
												   #no debemos mostrarle el boton de cierre de caja.
												   #cuando es 1, es que ya se ha guardado al menos una vez, y ya podemos mostrar el boton de cerrar caja.

	def __str__(self):
		estatus="CERRADA"
		if self.fecha_cierre==None:
			estatus="Abierta"

		return str(self.fecha)+' '+estatus

class Otros_Ingresos(models.Model):
	folio=models.CharField(max_length=7,null=True)
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento,on_delete=models.PROTECT)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)
	fecha=models.DateTimeField(default=timezone.now)
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
	importe=models.IntegerField(default=0, validators=[MinValueValidator(Decimal('1'))])
	comentario=models.CharField(max_length=200,default='')
	caja=models.CharField(max_length=1,null=True)

class Retiro_Efectivo(models.Model):
	folio=models.CharField(max_length = 7,null = True)
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento,on_delete = models.PROTECT)
	sucursal=models.ForeignKey(Sucursal,on_delete = models.PROTECT)
	fecha=models.DateTimeField(default = timezone.now)
	usuario=models.ForeignKey(User,on_delete = models.PROTECT,related_name = "usuario_alta")
	importe=models.IntegerField(default = 0, validators = [MinValueValidator(Decimal('1'))])
	comentario=models.TextField(default = '')
	caja=models.CharField(max_length = 1,null = True)
	token=models.IntegerField()
	concepto = models.ForeignKey(Concepto_Retiro,on_delete = models.PROTECT,blank = True,null = True)
	#no requerimos fecha de cancelacion ya que solo se puede cancelar el dia en que se genera.
	usuario_cancela = models.ForeignKey(User,on_delete = models.PROTECT,null = True, blank = True,related_name = 'usuario_cancela')
	activo = models.CharField(choices = SI_NO,default = 1, max_length=2)


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
	tipo_producto=models.ForeignKey(Tipo_Producto,on_delete=models.PROTECT,blank=True,null=False)
	kilataje=models.CharField(max_length=10,null=False)
	avaluo=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	tipo_kilataje=models.ForeignKey(Tipo_Kilataje,on_delete=models.PROTECT,blank=True,null=True)
	activo=models.CharField(max_length=1,default="S")
	
	def __str__(self):
		return self.tipo_producto.tipo_producto+' '+self.kilataje+' $'+str(self.avaluo)

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
	nombre=models.CharField(max_length=20,null=False)
	apellido_p=models.CharField(max_length=20,null=False)
	apellido_m=models.CharField(max_length=20,default='',null=True)
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

	def __str__(self):
		return self.nombre+' '+self.apellido_p+' '+self.apellido_m


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
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
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
	estatus=models.ForeignKey(Estatus_Boleta,on_delete=models.PROTECT,default=1)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT,blank=True,null=True)
	mutuo_original=models.IntegerField(default=0)	#este campo no se actualiza, nos sirve para saber cual fue el mutuo original de la boleta.
	fecha_vencimiento_real=models.DateTimeField(null=True,blank=True)#cuando la fecha de vencimiento cai en dia de asueto, la fecha de vencimienot se recorre un dia, esta fecha nos indica cual es la fecha de vencimiento real para calcular el las futuras fechas de vencimiento.
	
	almacenaje = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0)
	interes = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0)
	iva = models.DecimalField(max_digits = 20,decimal_places = 2,default = 0)



	@classmethod
	def nuevo_empeno(self,sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus,folio,tm):

		boleta = self.objects.create(folio = folio,tipo_producto = tp,caja = caja,usuario = usuario,avaluo = avaluo,mutuo = mutuo,fecha = timezone.now(),fecha_vencimiento = fecha_vencimiento,cliente = cliente,nombre_cotitular = nombre_cotitular,apellido_p_cotitular = apellido_paterno,apellido_m_cotitular = apellido_materno,plazo = plazo,sucursal = sucursal,mutuo_original = mutuo,fecha_vencimiento_real = fecha_vencimiento_real,estatus = estatus,almacenaje =  sucursal.fn_get_almacenaje(tp.id), interes = sucursal.fn_get_interes(tp.id),iva = sucursal.fn_get_iva(tp.id))
				
		return boleta	
			
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

class Abono(models.Model):
	folio=models.CharField(max_length=7,null=True)
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento,on_delete=models.PROTECT,null=True,blank=True)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT,null=True,blank=True)	
	fecha=models.DateTimeField(default=timezone.now)
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
	importe=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)	
	caja=models.ForeignKey(Cajas,on_delete=models.PROTECT,blank=True,null=True)
	boleta=models.ForeignKey(Boleta_Empeno,on_delete=models.PROTECT,blank=True,null=True)




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









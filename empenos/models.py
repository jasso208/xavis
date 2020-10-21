from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from seguridad.models import Session
from datetime import date, datetime, time,timedelta
import calendar
from django.db.models import Sum


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
	porcentaje=models.IntegerField()#este es el procentaje para venta
	porcentaje_apartado=models.IntegerField(default=0)#es el porcentaje para apartado


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

	@classmethod
	def nuevo_empeno(self,sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus,folio,tm):

		
	

		boleta = self.objects.create(folio = folio,tipo_producto = tp,caja = caja,usuario = usuario,avaluo = avaluo,mutuo = mutuo,fecha = timezone.now(),fecha_vencimiento = fecha_vencimiento,cliente = cliente,nombre_cotitular = nombre_cotitular,apellido_p_cotitular = apellido_paterno,apellido_m_cotitular = apellido_materno,plazo = plazo,sucursal = sucursal,mutuo_original = mutuo,fecha_vencimiento_real = fecha_vencimiento_real,estatus = estatus)
				
		return boleta	
				


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









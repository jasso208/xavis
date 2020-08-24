from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from seguridad.models import Session


GENERO_CHOICES = (
    ('1','HOMBRE'),
    ('2', 'MUJER'),
    
)

ESTADO_CIVIL_CHOICES = (
    ('1','SOLTERO'),
    ('2', 'CASADO'),
)





class Tipo_Movimiento(models.Model):
	tipo_movimiento=models.CharField(max_length=50,null=False)
	naturaleza=models.CharField(max_length=20,null=False)

	def __str__(self):
		return self.tipo_movimiento+' - '+self.naturaleza



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
		return self.sucursal


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
	folio=models.CharField(max_length=7,null=True)
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento,on_delete=models.PROTECT)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)
	fecha=models.DateTimeField(default=timezone.now)
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
	importe=models.IntegerField(default=0, validators=[MinValueValidator(Decimal('1'))])
	comentario=models.TextField()
	caja=models.CharField(max_length=1,null=True)
	token=models.IntegerField()

class Token(models.Model):
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento,on_delete=models.PROTECT)
	sucursal=models.ForeignKey(Sucursal,on_delete=models.PROTECT)
	caja=models.CharField(max_length=1,null=True)
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
	token=models.IntegerField()
	fecha=models.DateTimeField(default=timezone.now)

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

	class Meta:
		unique_together=("folio",'sucursal',)


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








from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from inventario.models import Productos,Tallas
from seguridad.models import Cliente
from django.utils import timezone
class Carrito_Compras(models.Model):
	session=models.CharField(max_length=18,null=False)
	id_producto=models.ForeignKey(Productos,on_delete=models.PROTECT)
	cantidad=models.IntegerField(null=False)
	talla=models.ForeignKey(Tallas,on_delete=models.PROTECT)
	
	def __str__(self):
		return self.session
	
class Estatus_Venta(models.Model):
	estatus_venta=models.CharField(max_length=30,null=False)
	
	def __str__(self):
		return self.estatus_venta
		
class Venta(models.Model):
	fecha=models.DateTimeField(default=timezone.now())
	sub_total=models.DecimalField(max_digits=20,decimal_places=2,null=False)
	descuento=models.DecimalField(max_digits=20,decimal_places=2,null=False,default=0)
	iva=models.DecimalField(max_digits=20,decimal_places=2,null=False)	
	total=models.DecimalField(max_digits=20,decimal_places=2,null=False)
	id_estatus_venta=models.ForeignKey(Estatus_Venta,on_delete=models.PROTECT,default=1)
	link_seguimiento=models.CharField(max_length=200,null=True,default='No Disponible')
	cliente=models.ForeignKey(Cliente,on_delete=models.PROTECT,default=1)
	
class Detalle_Venta(models.Model):
	id_venta=models.ForeignKey(Venta,on_delete=models.PROTECT)
	id_producto=models.ForeignKey(Productos,on_delete=models.PROTECT,null=False)
	cantidad=models.IntegerField(null=False)
	talla=models.ForeignKey(Tallas,on_delete=models.PROTECT,null=False)
	precio_unitario=models.DecimalField(max_digits=20,decimal_places=2,null=False)#almacena el precio antes de descuento e impuesto
	descuento=models.DecimalField(max_digits=20,decimal_places=2,null=False,default=0.00)#almacena el importe de descuento
	iva=models.DecimalField(max_digits=20,decimal_places=2,null=False,default=0.00)#almacena el iva
	precio_total=models.DecimalField(max_digits=20,decimal_places=2,null=False)#almacena el precio de todos los productos (precio_unitario*cantidad)
	
class Direccion_Envio_Venta(models.Model):
	id_venta=models.ForeignKey(Venta,on_delete=models.PROTECT)
	nombre_recibe=models.CharField(max_length=20,null=False)
	apellido_p=models.CharField(max_length=20,null=False)
	apellido_m=models.CharField(max_length=20)
	calle=models.CharField(max_length=50,null=False)
	numero_interior=models.CharField(max_length=10,null=True)	
	numero_exterior=models.CharField(max_length=10,null=True)	
	cp=models.CharField(max_length=10,null=False)	
	municipio=models.CharField(max_length=50,null=False,default="")
	estado=models.CharField(max_length=50,null=False,default="")
	pais=models.CharField(max_length=50,null=False,default="")
	telefono=models.CharField(max_length=20,null=False)
	correo_electronico=models.CharField(max_length=50,null=False)
	referencia=models.CharField(max_length=200,null=False)
	
	
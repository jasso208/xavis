from django.db import models
from django.utils import timezone
from datetime import datetime

class Estatus(models.Model):	
	estatus=models.CharField(max_length=20)
	
	def __str__(self):
		return self.estatus
		
class Productos(models.Model):	
	nombre=models.CharField(max_length=100)
	desc_producto=models.TextField()
	precio=models.DecimalField(max_digits=26,decimal_places=2,default=0.00)
	descuento=models.IntegerField(default=0)
	id_estatus=models.ForeignKey(Estatus,on_delete=models.PROTECT)
	
	def __str__(self):
		return str(self.id)+' '+self.nombre
		
class Atributos(models.Model):
	id_producto=models.ForeignKey(Productos,on_delete=models.PROTECT)
	atributo=models.CharField(max_length=50)
	valor_atributo=models.CharField(max_length=50)
	
	def __str__(self):
		return self.atributo
	
class Tallas(models.Model):
	id_producto=models.ForeignKey(Productos,on_delete=models.PROTECT)
	talla=models.CharField(max_length=10)
	
	def __str__(self):
		return str(self.id)+' '+self.id_producto.nombre+' '+self.talla
		
	
class Img_Producto(models.Model):
	id_producto=models.ForeignKey(Productos,on_delete=models.PROTECT)
	nom_img=models.CharField(max_length=20)
	orden=models.IntegerField()
	def __str__(self):
		return self.nom_img

class Productos_Relacionados(models.Model):
	id_producto=models.ForeignKey(Productos,on_delete=models.PROTECT,related_name='producto')
	id_producto_relacionado=models.ForeignKey(Productos,on_delete=models.PROTECT,related_name='prod_relacionado')
	
	def __str__(self):
		return self.id_producto.nombre+'=>'+self.id_producto_relacionado.nombre

class Carrito_Compras(models.Model):
	session=models.CharField(max_length=18,null=False)
	id_producto=models.ForeignKey(Productos,on_delete=models.PROTECT)
	cantidad=models.IntegerField(null=False)
	talla=models.ForeignKey(Tallas,on_delete=models.PROTECT)
	
	def __str__(self):
		return self.session
		
class Municipio(models.Model):
	municipio=models.CharField(max_length=50,null=False)
	
class Estado(models.Model):
	estado=models.CharField(max_length=50,null=False)
	
class Pais(models.Model):
	pais=models.CharField(max_length=50,null=False)
	
class Direccion_Envio(models.Model):
	session=models.CharField(max_length=18,null=False)
	nombre=models.CharField(max_length=20,null=False) #es el nombre de quien recibe
	apellido_p=models.CharField(max_length=20,null=False)
	apellido_m=models.CharField(max_length=20)
	calle=models.CharField(max_length=50,null=False)
	numero=models.CharField(max_length=10,null=False)	
	cp=models.CharField(max_length=10,null=False)	
	municipio=models.CharField(max_length=50,null=False,default="")
	estado=models.CharField(max_length=50,null=False,default="")
	pais=models.CharField(max_length=50,null=False,default="")
	telefono=models.CharField(max_length=20,null=False)
	correo_electronico=models.CharField(max_length=50,null=False)
	referencia=models.CharField(max_length=200,null=False)
	
	def __str__(self):
		return self.session
	
class Categorias(models.Model):
	categoria=models.CharField(max_length=10,null=False)
	
	def __str__(self):
		return str(self.id)+' '+self.categoria
	
class Rel_Producto_Categoria(models.Model):
	id_producto=models.ForeignKey(Productos,on_delete=models.PROTECT)
	id_categoria=models.ForeignKey(Categorias,on_delete=models.PROTECT)
	
	def __str__(self):
		return "["+str(self.id_categoria.id)+' '+self.id_categoria.categoria+'] '+self.id_producto.nombre

class Venta(models.Model):
	fecha=models.DateTimeField(default=datetime.now())
	sub_total=models.DecimalField(max_digits=20,decimal_places=2,null=False)
	descuento=models.DecimalField(max_digits=20,decimal_places=2,null=False,default=0)
	iva=models.DecimalField(max_digits=20,decimal_places=2,null=False)	
	total=models.DecimalField(max_digits=20,decimal_places=2,null=False)

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
	numero=models.CharField(max_length=10,null=False)	
	cp=models.CharField(max_length=10,null=False)	
	municipio=models.CharField(max_length=50,null=False,default="")
	estado=models.CharField(max_length=50,null=False,default="")
	pais=models.CharField(max_length=50,null=False,default="")
	telefono=models.CharField(max_length=20,null=False)
	correo_electronico=models.CharField(max_length=50,null=False)
	referencia=models.CharField(max_length=200,null=False)
	

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Tipo_Movimiento(models.Model):
	tipo_movimiento=models.CharField(max_length=50,null=False)
	naturaleza=models.CharField(max_length=20,null=False)

class Perfil(models.Model):
	perfil=models.CharField(max_length=30,null=False)

class Sucursal(models.Model):
	sucursal=models.CharField(max_length=100,null=False)
	calle=models.CharField(max_length=50,null=True)
	numero=models.IntegerField(null=True)
	colonia=models.CharField(max_length=50,null=True)
	estado=models.CharField(max_length=50,null=True)
	pais=models.CharField(max_length=50,null=True)

#esta tabla es un complemento de la tabla user de django.
class User_2(models.Model):
	user=models.ForeignKey(User)
	sucursal=models.ForeignKey(Sucursal)
	perfil=models.ForeignKey(Perfil)

class Control_Folios(models.Model):
	folio=models.IntegerField(null=False)
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento)
	sucursal=models.ForeignKey(Sucursal)

class Cliente(models.Model):
	nombre=models.CharField(max_length=50,null=False)
	apellido_p=models.CharField(max_length=50,null=False)
	apellido_m=models.CharField(max_length=50,null=False)
	#falta agregar el resto de los campos

class Cajas(models.Model):
	folio=models.CharField(max_length=7,null=False)
	tipo_movimiento=models.ForeignKey(Tipo_Movimiento)
	sucursal=models.ForeignKey(sucursal)
	fecha=models.DateTimeField(default=timezone.now())
	usuario=models.ForeignKey(User)
	importe=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	caja=models.CharField(max_length=1,null=False)
	real_tarjeta=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	real_efectivo=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	teorico_tarjeta=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	teorico_efectivo=mdoels.DecimalField(max_digits=20,decimal_places=2,default=0.00)
	diferencia=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
#tabla de clientes
class Cliente(models.Model):
	nombre=models.CharField(max_length=20,null=False) #es el nombre de quien recibe
	apellido_p=models.CharField(max_length=20,null=False)
	apellido_m=models.CharField(max_length=20)
	telefono=models.CharField(max_length=10)
	e_mail=models.CharField(max_length=50,unique=True)
	rfc=models.CharField(max_length=13,null=True)
	psw=models.CharField(max_length=10)
	
class Direccion_Envio_Cliente(models.Model):
	cliente=models.ForeignKey(Cliente,on_delete=models.PROTECT,default=2)	
	calle=models.CharField(max_length=50,null=False)
	numero_interior=models.CharField(max_length=10,null=False)	
	numero_exterior=models.CharField(max_length=10,null=False)
	cp=models.CharField(max_length=10,null=False)	
	municipio=models.CharField(max_length=50,null=False,default="")
	estado=models.CharField(max_length=50,null=False,default="")
	pais=models.CharField(max_length=50,null=False,default="")	
	referencia=models.CharField(max_length=200,null=False)

#cuando un cliente de autentica correctamente guardaremos en estado
#tabla el token (session) generdo en el front end y el usuario que se autentico con ese token.
#para que en posteriores movimientos de ese token, identificar a que cliente le pertenece.
class Clientes_Logueados(models.Model):
	cliente=models.ForeignKey(Cliente,on_delete=models.PROTECT)
	session=models.CharField(max_length=18,null=False)
	
#cuando el cliente no este logueado o este logueado e intente enviar su pedido
#a otra direccion, aqui se almacenara.
#de esta tabla se tomara la informacion para guardar en la venta
class Direccion_Envio_Cliente_Temporal(models.Model):
	session=models.CharField(max_length=18,null=False)	
	nombre=models.CharField(max_length=20,null=False) #es el nombre de quien recibe
	apellido_p=models.CharField(max_length=20,null=False)
	apellido_m=models.CharField(max_length=20)
	telefono=models.CharField(max_length=10)
	e_mail=models.CharField(max_length=50)
	rfc=models.CharField(max_length=13,null=True)	
	calle=models.CharField(max_length=50,null=False)
	numero_interior=models.CharField(max_length=10,null=False)	
	numero_exterior=models.CharField(max_length=10,null=False)
	cp=models.CharField(max_length=10,null=False)	
	municipio=models.CharField(max_length=50,null=False,default="")
	estado=models.CharField(max_length=50,null=False,default="")
	pais=models.CharField(max_length=50,null=False,default="")	
	referencia=models.CharField(max_length=200,null=False)
	
#Aqui se registran los E-Mails para enviar promociones y ofertas	
class E_Mail_Notificacion(models.Model):
	e_mail=models.CharField(max_length=50)
	
#en esta tabla se almacen el imail y la session de los que quieren recuperar el password,
#tendra una vida de 24 horas, despues de ese tiempo, sera borrado por un proceso automatico.
class Recupera_pws(models.Model):
	e_mail=models.CharField(max_length=50,null=False)
	session=models.CharField(max_length=18,null=False)
	fecha=models.DateField(default=timezone.now)
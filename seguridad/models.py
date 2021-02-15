from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

#Almacenamos la seccion del sistema que deseamos administrar
#por ejemplo: En el menu Administracion esta la opcion, alta de sucursal, baja de sucursal, etc
#en el ejemplo la seccion sera Administracion
class Seccion(models.Model):	
	desc_seccion = models.CharField(max_length  = 50,null = False)

	def __str__(self):
		return str(self.id) + ' ' + self.desc_seccion

class Menu(models.Model):
	desc_item = models.CharField(max_length = 50,null = False)
	vista = models.CharField(max_length = 50,null = False) #la vista a la que hace referencia
	app = models.CharField(max_length = 50,null = False)#la appa  ala que pertenece la vista.
	seccion = models.ForeignKey(Seccion,on_delete = models.PROTECT,null = False,blank = False) #la seccion a la que pertenece la vista.

	def __str__(self):
		return str(self.id) + ' ' + self.desc_item

#almacenamos a que vistas tiene acceso el usuario
class Permisos_Usuario(models.Model):
	usuario = models.ForeignKey(User,on_delete = models.PROTECT,related_name = "usuario_permiso")
	opcion_menu = models.ForeignKey(Menu,on_delete = models.PROTECT)
	usuario_otorga = models.ForeignKey(User,on_delete = models.PROTECT,null = True,blank = True,related_name = "usuario_otorga")

	class Meta:
		unique_together = ('usuario','opcion_menu',)
	
	























"""
	*** DE aqui par abajo no se usa, pero lo conserve por si acaso.
"""
class Session(models.Model):
	usuario=models.ForeignKey(User,on_delete=models.PROTECT)
	sesion=models.IntegerField()

#tabla de clientes
"""class Cliente(models.Model):
	nombre=models.CharField(max_length=20,null=False) #es el nombre de quien recibe
	apellido_p=models.CharField(max_length=20,null=False)
	apellido_m=models.CharField(max_length=20)
	telefono=models.CharField(max_length=10)
	e_mail=models.CharField(max_length=50,unique=True)
	rfc=models.CharField(max_length=13,null=True)
	psw=models.CharField(max_length=10)
"""	
class Direccion_Envio_Cliente(models.Model):
	#cliente=models.ForeignKey(Cliente,on_delete=models.PROTECT,null=True)	
	calle=models.CharField(max_length=50,null=False)
	numero_interior=models.CharField(max_length=10,null=False)	
	numero_exterior=models.CharField(max_length=10,null=False)
	cp=models.CharField(max_length=10,null=False)	
	colonia=models.CharField(max_length=50,null=True)	
	municipio=models.CharField(max_length=50,null=False,default="")
	estado=models.CharField(max_length=50,null=False,default="")
	pais=models.CharField(max_length=50,null=False,default="")	
	referencia=models.CharField(max_length=200,null=False)



#cuando un cliente de autentica correctamente guardaremos en estado
#tabla el token (session) generdo en el front end y el usuario que se autentico con ese token.
#para que en posteriores movimientos de ese token, identificar a que cliente le pertenece.
class Clientes_Logueados(models.Model):
	#cliente=models.ForeignKey(Cliente,on_delete=models.PROTECT)
	session=models.CharField(max_length=18,null=False)
	
#cuando el cliente no este logueado o este logueado e intente enviar su pedido
#a otra direccion, aqui se almacenara.
#de esta tabla se tomara la informacion para guardar en la venta
class Direccion_Envio_Cliente_Temporal(models.Model):
	session=models.CharField(max_length=18,null=False)	
	nombre=models.CharField(max_length=20,null=False) #es el nombre de quien recibe
	apellido_p=models.CharField(max_length=20,null=False)
	apellido_m=models.CharField(max_length=20,null=True)
	telefono=models.CharField(max_length=10)
	e_mail=models.CharField(max_length=50)
	rfc=models.CharField(max_length=13,null=True)	
	calle=models.CharField(max_length=50,null=False)
	numero_interior=models.CharField(max_length=10,null=True)	
	numero_exterior=models.CharField(max_length=10,null=False)
	cp=models.CharField(max_length=10,null=False)
	colonia=models.CharField(max_length=50,null=True)	
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
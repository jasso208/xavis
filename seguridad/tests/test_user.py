from django.test import TestCase
from empenos.models import *
from seguridad.models import *
class User_Test(TestCase):
	#en esta funcion inicializamos todo lo necesario par alas pruebas,
	#se ejecuta cada vez que se corre una prueba unitaria
	@classmethod
	def setUpTestData(cls):
		User.objects.create(id = 1,username="jasso208")
		Sucursal.objects.create(sucursal="prueba")
		Perfil.objects.create(id = 1,perfil = "Valuador")
		usr2 = User_2()
		usr2.user = User.objects.get(username = "jasso208")
		usr2.sucursal = Sucursal.objects.get(sucursal = "prueba")
		usr2.perfil = Perfil.objects.get(perfil = "Valuador")
		usr2.usuario_alta = User.objects.get(username = "jasso208")
		usr2.save()

		sec = Seccion()
		sec.desc_seccion = "General"
		sec.save()

		men = Menu()
		men.id = 1#debemos indicar el id para asegurar que siempre sea el 1
		men.desc_item = "Prueba 1"
		men.vista  = "Prueba 1"
		men.app	=	"prueba"
		men.seccion = sec
		men.save()

		men = Menu()
		men.id = 2#debemos indicar el id para asegurar que siempre sea el 1
		men.desc_item = "Prueba 2"
		men.vista  = "Prueba 2"
		men.app	=	"prueba"
		men.seccion = sec
		men.save()


		

	"""
	******************************************************************************************************************+
	Validamos la asignacion de permisos a los usuarios

	******************************************************************************************************************+
	"""		
	##1.- El usuario debe estar activo para poder asignarle permisos.

	##asignar permisos
	def test_valida_usuario_valido(self):	
		
		usuario = User_2.objects.get(user__username = "jasso208")
		
		#desactivmamos el usuario para validar.
		usuario.user.is_active = False
		usuario.user.save()

		resp = usuario.fn_agrega_acceso_a_vista(1,1)
		self.assertEqual(False,resp[0])
		self.assertEqual("El usuario esta inactivo, no puede modificar sus permisos.",resp[1])


	##2.- El id de menu que se proporcione debe de existir en el catalogo de opciones del menu.
	def test_valida_menu_valido(self):
		usuario = User_2.objects.get(user__username = "jasso208")
		resp = usuario.fn_agrega_acceso_a_vista(100,1)
		
		self.assertEqual(False,resp[0])
		self.assertEqual("La opción que intenta agregar no existe o no es valida.",resp[1])

	##4.- El id de la vista debe ser entero
	def test_valida_menu_valido_2(self):
		usuario = User_2.objects.get(user__username = "jasso208")
		resp = usuario.fn_agrega_acceso_a_vista('e',1)
		
		self.assertEqual(False,resp[0])
		self.assertEqual("La opción que intenta agregar no existe o no es valida.",resp[1])


	##5.- Si se intenta agregar un permiso que ya existe, debera indicar que el permiso ya se agrego.
	def test_duplica_permiso_a_usuario(self):
		usuario = User_2.objects.get(user__username = "jasso208")
		resp = usuario.fn_agrega_acceso_a_vista(1,1)

		self.assertEqual(True,resp[0])
		self.assertEqual("Se actualizo correctamente.",resp[1])

		resp = usuario.fn_agrega_acceso_a_vista(1,1)
		self.assertEqual(True,resp[0])
		self.assertEqual("Se actualizo correctamente.",resp[1])


	##6 Se agregar permiso correctamente
	def test_agrega_permiso_ok(self):
		usuario = User_2.objects.get(user__username = "jasso208")
		resp = usuario.fn_agrega_acceso_a_vista(1,1)

		self.assertEqual(True,resp[0])
		self.assertEqual("Se actualizo correctamente.",resp[1])


	
	##remover permisos


	##6.- Si se intenta quitar un permiso 
	def test_valida_usuario_valido_remover_permiso(self):
		usuario = User_2.objects.get(user__username = "jasso208")
		#desactivmamos el usuario para validar.
		usuario.user.is_active = False
		usuario.user.save()

		resp = usuario.fn_remover_acceso_a_vista(1)
		self.assertEqual(False,resp[0])
		self.assertEqual("El usuario esta inactivo, no puede modificar sus permisos.",resp[1])


	##2.- El id de menu que se proporcione debe de existir en el catalogo de opciones del menu.
	def test_valida_menu_valido_remover_permis(self):
		usuario = User_2.objects.get(user__username = "jasso208")
		resp = usuario.fn_remover_acceso_a_vista(100)
		self.assertEqual(True,resp[0])
		self.assertEqual("Se actualizo correctamente.",resp[1])

	##4.- El id de la vista debe ser entero
	def test_valida_menu_valido_2_remover_permis(self):
		usuario = User_2.objects.get(user__username = "jasso208")
		resp = usuario.fn_remover_acceso_a_vista('e')
		
		self.assertEqual(True,resp[0])
		self.assertEqual("Se actualizo correctamente.",resp[1])


	##5.- Si se intenta remover un permiso que ya existe, debera indicar que el permiso ya se removio.
	def test_duplica_permiso_a_usuario_remover_permis(self):
		usuario = User_2.objects.get(user__username = "jasso208")
		resp = usuario.fn_remover_acceso_a_vista(1)

		self.assertEqual(True,resp[0])
		self.assertEqual("Se actualizo correctamente.",resp[1])

		resp = usuario.fn_remover_acceso_a_vista(1)
		self.assertEqual(True,resp[0])
		self.assertEqual("Se actualizo correctamente.",resp[1])

	def test_remover_permiso_ok(self):
		usuario = User_2.objects.get(user__username = "jasso208")
		#agregamos el permiso
		resp = usuario.fn_agrega_acceso_a_vista(1,1)
		#removemos el permiso
		resp = usuario.fn_remover_acceso_a_vista(1)		


		self.assertEqual(True,resp[0])
		self.assertEqual("Se actualizo correctamente.",resp[1])




	"""
	******************************************************************************************************************+
	Validamos la asignacion de permisos a los usuarios

	******************************************************************************************************************+
	"""
	#Validamos que el usuario tenga permiso o no a una ruta
	##1: Se agregan permiso a la opcion 1 y no a la opcion 2	
	def test_valida_acceso_a_opcion(self):
		usuario = User_2.objects.get(user__username = "jasso208")
		resp = usuario.fn_agrega_acceso_a_vista(1,1)

		resp1 = usuario.fn_tiene_acceso_a_vista(1)
		resp2 = usuario.fn_tiene_acceso_a_vista(2)		

		self.assertEqual(False,resp2)
		self.assertEqual(True,resp1)
	##2: Se agrega permiso a laopcion 1 y 2, y posteriormente se elimina el permiso de la opcion 2
	def test_valida_acceso_a_opcion_2(self):
		usuario = User_2.objects.get(user__username = "jasso208")

		usuario.fn_agrega_acceso_a_vista(1,1)
		usuario.fn_agrega_acceso_a_vista(2,1)

		resp1 = usuario.fn_tiene_acceso_a_vista(1)
		resp2 = usuario.fn_tiene_acceso_a_vista(2)	

		self.assertEqual(True,resp1)
		self.assertEqual(True,resp2)

		#removemos el acceso a la opcion 2, ahora solo puede acceder a la opcion 1
		usuario.fn_remover_acceso_a_vista(2)
		resp3 = usuario.fn_tiene_acceso_a_vista(1)			
		resp4 = usuario.fn_tiene_acceso_a_vista(2)			
		
		self.assertEqual(True,resp3)
		self.assertEqual(False,resp4)


		






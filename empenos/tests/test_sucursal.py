from django.test import TestCase
from empenos.models import *

class Sucursal_Test(TestCase):
	@classmethod
	def setUpTestData(cls):		
		#creamos los catalogos
		User.objects.create(username="usuario_virtual")
		User.objects.create(username="jasso208")
		Sucursal.objects.create(sucursal="prueba")

		Tipo_Movimiento.objects.create(id = 1,tipo_movimiento="APERTURA DE CAJA")
		


	def test_valida_usuario_virtual(self):
		sucursal = Sucursal.objects.get(sucursal = "prueba")
		usuario_abre = User.objects.get(username = "jasso208")

		r = sucursal.fn_abre_caja(0,usuario_abre)
		self.assertEqual(False,r[0])
		self.assertEqual("La sucursal no tiene asignado usuario virtual, contacte con el administrador del sistema.",r[1])

	def test_valida_solo_1_caja_abierta(self):
		sucursal = Sucursal.objects.get(sucursal = "prueba")
		usuario_abre = User.objects.get(username = "jasso208")
		sucursal.usuario_virtual = User.objects.get(username = "usuario_virtual")
		sucursal.save()
		r = sucursal.fn_abre_caja(0,usuario_abre)
		
		self.assertEqual(True,r[0])

		r2 = sucursal.fn_abre_caja(0,usuario_abre)
		self.assertEqual(False,r2[0])		
		self.assertEqual("La sucursal cuenta con caja abierta. Solo puede abrir una caja por sucursal.",r2[1])


	#como es la primera vez que se apertura caja, se debe aperturar con importe cero
	def test_valida_importe_apertura(self):
		sucursal = Sucursal.objects.get(sucursal = "prueba")
		usuario_abre = User.objects.get(username = "jasso208")
		sucursal.usuario_virtual = User.objects.get(username = "usuario_virtual")
		sucursal.save()

		#como es la primera vez que se apertura caja, debe aperturarse con importe 0
		r = sucursal.fn_abre_caja(10,usuario_abre)				
		self.assertEqual(False,r[0])
		self.assertEqual("El importe con el que desea aperturar, es diferente al importe con el que cerro la ùltima caja.",r[1])

	#la apertura de caja, debe coincidir con el importe de la ultima caja abierta.
	def test_valida_importe_apertura_2(self):
		sucursal = Sucursal.objects.get(sucursal = "prueba")
		usuario_abre = User.objects.get(username = "jasso208")
		sucursal.usuario_virtual = User.objects.get(username = "usuario_virtual")
		sucursal.save()

		r = sucursal.fn_abre_caja(0,usuario_abre)			

		#cerramos todas la cajas
		for c in Cajas.objects.all():
			c.fecha_cierre = c.fecha
			c.teorico_efectivo = 10
			c.save()

		r = sucursal.fn_abre_caja(1,usuario_abre)	

		self.assertEqual(False,r[0])
		self.assertEqual("El importe con el que desea aperturar, es diferente al importe con el que cerro la ùltima caja.",r[1])


	#validamos que solo se abra una caja por dia (caja abierta)
	def test_valida_caja_solo_1_caja_x_dia(self):		
		sucursal = Sucursal.objects.get(sucursal = "prueba")
		usuario_abre = User.objects.get(username = "jasso208")
		sucursal.usuario_virtual = User.objects.get(username = "usuario_virtual")
		sucursal.save()

		r = sucursal.fn_abre_caja(0,usuario_abre)	

		#cerramos todas la cajas
		for c in Cajas.objects.all():
			c.fecha_cierre = c.fecha
			c.teorico_efectivo = 10
			c.save()
		sucursal.saldo =10
		sucursal.save()
		self.assertEqual(True,r[0])

		r2 = sucursal.fn_abre_caja(10,usuario_abre)	

		self.assertEqual(False,r2[0])
		self.assertEqual("La caja de esta sucursal ya fue cerrada.",r2[1])

	#se abre caja correctamente
	def test_abre_caja_con_exito(self):		
		sucursal = Sucursal.objects.get(sucursal = "prueba")
		usuario_abre = User.objects.get(username = "jasso208")
		sucursal.usuario_virtual = User.objects.get(username = "usuario_virtual")
		sucursal.save()

		r = sucursal.fn_abre_caja(0,usuario_abre)	
		caja = sucursal.fn_get_caja_abierta()

		self.assertEqual(True,r[0])
		self.assertEqual(caja.usuario,User.objects.get(username = "usuario_virtual"))
		self.assertEqual(caja.usuario_real_abre_caja,User.objects.get(username = "jasso208"))









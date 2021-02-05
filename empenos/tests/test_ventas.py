from django.test import TestCase
from empenos.models import *

class Ventas_Test():
	@classmethod
	def setUpTestData(cls):
		hoy = date.today()
		"""
			Creamos catalogos
		"""
		Sucursal.objects.create(sucursal="prueba")
		Tipo_Producto.objects.create(id = 1,tipo_producto="oro")

		User.objects.create(username="jasso208")
		Cliente.objects.create(id = 1,nombre="prueba",apellido_p="prueba",estado_civil=1)
		Plazo.objects.create(id = 1,plazo="4 semanas")

		Tipo_Pago.objects.create(id = 1,tipo_pago = "Refrendo")
		Tipo_Pago.objects.create(id = 2,tipo_pago = "Comision pg")
		Tipo_Pago.objects.create(id = 3,tipo_pago = "Refrendo PG")
		Estatus_Boleta.objects.create(id = 1,estatus="ABIERTA")
		Estatus_Boleta.objects.create(id = 2,estatus="CANCELADA")
		Estatus_Boleta.objects.create(id = 3,estatus="ALMONEDA")
		Estatus_Boleta.objects.create(id = 4,estatus="DESEMPEÑADA")
		Estatus_Boleta.objects.create(id = 5,estatus="REMATE")
		Estatus_Boleta.objects.create(id = 6,estatus="VENDIDA")
		Estatus_Boleta.objects.create(id = 7,estatus="APARTADA")

		Tipo_Movimiento.objects.create(id = 1,tipo_movimiento="APERTURA DE CAJA")
		Tipo_Movimiento.objects.create(id = 2,tipo_movimiento="OTROS INGRESOS")
		Tipo_Movimiento.objects.create(id = 3,tipo_movimiento="RETIRO EFECTIVO")
		Tipo_Movimiento.objects.create(id = 4,tipo_movimiento="BOLETA EMPEÑO")
		Tipo_Movimiento.objects.create(id = 5,tipo_movimiento="REFRENDO")
		Tipo_Movimiento.objects.create(id = 6,tipo_movimiento="VENTA PISO")
		Tipo_Movimiento.objects.create(id = 7,tipo_movimiento="APARTADO")
		Tipo_Movimiento.objects.create(id = 8,tipo_movimiento="ABONO APARTADO")

		Estatus_Apartado.objects.create(id = 1,estatus="apartado")
		Estatus_Apartado.objects.create(id = 2,estatus="liberado")
		Estatus_Apartado.objects.create(id = 3,estatus="vendido")




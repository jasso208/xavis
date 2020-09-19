from django.test import TestCase
from empenos.jobs import *

from empenos.models import *
from datetime import date, datetime, time,timedelta
# Create your tests here.

#probamos el job para liberar los apartados que se vencen y no ha sido cubierto su saldo restante
class TestJobApartado(TestCase):
	#aqui se inicializan los valores de la prueba, tipo un constructor
	def setUpTestData(cls):
		hoy = date.today()

		Sucursal.objects.create(sucursal="prueba")
		Tipo_Producto.objects.create(tipo_producto="oro")
		User.objects.create(username="jasso208")
		Cliente.objects.create(nombre="prueba",apellido_p="prueba",estado_civil=1)
		Plazo.objects.create(plazo="4 semanas")
		Estatus_Boleta.objects.create(estatus="ABIERTA")
		Estatus_Boleta.objects.create(estatus="CANCELADA")
		Estatus_Boleta.objects.create(estatus="ALMONEDA")
		Estatus_Boleta.objects.create(estatus="DESEMPEÑADA")
		Estatus_Boleta.objects.create(estatus="REMATE")
		Estatus_Boleta.objects.create(estatus="VENDIDA")
		Estatus_Boleta.objects.create(estatus="APARTADA")

		Tipo_Movimiento.objects.create(tipo_movimiento="APERTURA DE CAJA")
		Tipo_Movimiento.objects.create(tipo_movimiento="OTROS INGRESOS")
		Tipo_Movimiento.objects.create(tipo_movimiento="RETIRO EFECTIVO")
		Tipo_Movimiento.objects.create(tipo_movimiento="BOLETA EMPEÑO")
		Tipo_Movimiento.objects.create(tipo_movimiento="REFRENDO")
		Tipo_Movimiento.objects.create(tipo_movimiento="VENTA PISO")
		Tipo_Movimiento.objects.create(tipo_movimiento="APARTADO")
		Tipo_Movimiento.objects.create(tipo_movimiento="ABONO APARTADO")

		Estatus_Apartado.objects.create(estatus="apartado")
		Estatus_Apartado.objects.create(estatus="liberado")
		Estatus_Apartado.objects.create(estatus="vendido")
		
		un_dia=timedelta(days=1)

		for x in Tipo_Movimiento.objects.all():
			print(x.id)
			print(x.tipo_movimiento)
			print("")
		tm = Tipo_Movimiento.objects.get(id=4)
		#creamos una boleta para la prueba		
		sucursal = Sucursal.objects.get(id = 1)
		tp = Tipo_Producto.objects.get(id = 1)
		caja = None
		usuario = User.objects.get(id=1)
		avaluo = 0
		mutuo = 0
		fecha_vencimiento = datetime.combine(hoy,time.min)#para la prueba  no importa la fecha de vencimiento
		cliente = Cliente.objects.get(id=1)
		nombre_cotitular = "test_1"
		apellido_paterno = ""
		apellido_materno = ""

		plazo=Plazo.objects.get(id=1)
		fecha_vencimiento_real = fecha_vencimiento

		estatus_boleta = Estatus_Boleta.objects.get(id=7)
		estatus_apartado = Estatus_Apartado.objects.get(id=1)



		#la boleta con folio 1 vence hoy mismo
		boleta = Boleta_Empeno.nuevo_empeno(sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus_boleta,1,tm)

		apartado=Apartado()
		apartado.folio=1
		apartado.usuario=usuario
		
		apartado.importe_venta=1000
		apartado.caja=None
		apartado.cliente=cliente
		apartado.saldo_restante=10
		apartado.estatus=estatus_apartado
		apartado.boleta=boleta
		apartado.fecha_vencimiento=fecha_vencimiento
		apartado.sucursal=sucursal
		apartado.save()

		

		#la boleta con folio 2 no venve hoy, asi que no la afecta
		boleta = Boleta_Empeno.nuevo_empeno(sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus_boleta,2,tm)

		apartado=Apartado()
		apartado.folio=2
		apartado.usuario=usuario
		
		apartado.importe_venta=1000
		apartado.caja=None
		apartado.cliente=cliente
		apartado.saldo_restante=10
		apartado.estatus=estatus_apartado
		apartado.boleta=boleta
		apartado.fecha_vencimiento=fecha_vencimiento+un_dia
		apartado.sucursal=sucursal
		apartado.save()

		return True


	def test_apartado_vence_hoy(self):
		estatus_liberado = Estatus_Apartado.objects.get(id=2)
		estatus_remate = Estatus_Boleta.objects.get(id=5)	


		fn_job_libera_apartado()
		
		apartado = Apartado.objects.get(id = 1)		
		boleta = Boleta_Empeno.objects.get(id = 1)


		self.assertEqual(apartado.estatus,estatus_liberado)
		self.assertEqual(apartado.boleta,None)
		self.assertEqual(boleta.estatus,estatus_remate)


	def test_apartado_no_vence_hoy(self):
		estatus_boleta_apartado = Estatus_Boleta.objects.get(id=7)
		estatus_apartado_apartado = Estatus_Apartado.objects.get(id=1)

		apartado_2 = Apartado.objects.get(id = 2)
		boleta_2 = Boleta_Empeno.objects.get(id = 2)

		self.assertEqual(apartado_2.estatus,estatus_apartado_apartado)
		self.assertEqual(apartado_2.boleta,boleta_2)
		self.assertEqual(boleta_2.estatus,estatus_boleta_apartado)



		













	





from django.test import TestCase
from empenos.jobs import *

from empenos.models import *
from datetime import date, datetime, time,timedelta

class BoletaEmpenoTestCase(TestCase):

	#Inicializamos los objetos
	#estos objetos se recrean a cada prueba que se ejecuta.
	#se eliminan en la funcion TearDown
	def setUp(self):
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

		tm = Tipo_Movimiento.objects.get(id=4)

		usuario = User.objects.get(username="jasso208")

		#creamos una boleta para la prueba		
		sucursal = Sucursal.objects.get(sucursal = "prueba")

		cie = Configuracion_Interes_Empeno()

		cie.sucursal = sucursal		
		cie.almacenaje_oro = 10
		cie.interes_oro = 20
		cie.iva_oro = 30
		cie.almacenaje_plata = 15
		cie.interes_plata = 25
		cie.iva_plata = 35
		cie.almacenaje_prod_varios = 5
		cie.interes_prod_varios = 6
		cie.iva_prod_varios = 7
		cie.usuario_modifica = usuario
		cie.save()



		tp = Tipo_Producto.objects.get(id = 1)
		caja = None
		
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


	#eliminamos los objetos creados en la funcion setUp
	def tearDown(self):							Estatus_Apartado.objects.all().delete()
		User.objects.all().delete()		
		Tipo_Movimiento.objects.all().delete()
		#creamos una boleta para la prueba		
		Sucursal.objects.all().delete()
		Configuracion_Interes_Empeno.objects.all().delete()
		Tipo_Producto.objects.all().delete()		
		Cliente.objects.all().delete()		
		Plazo.objects.all().delete()
		Estatus_Boleta.objects.all().delete()		
		
		Apartado.objects.all().delete()


	#Prueba 1: aplicar refrendo: Boleta activa, refrendo el dia en que se genero la boleta.
	def test_aplica_abono_1(self):
		print("empezo 1")
		tm = Tipo_Movimiento.objects.all()
		for t in tm:
			print(t.id)
			print(t.tipo_movimiento)

		print("termino 1 ")
		return True
	#Prueba 2: aplicar refrendo: Boleta activa, refrendo al dia siguiente despues de vencer la primera semana.
	def test_aplica_abono_2(self):
		print("empezo 2")
		tm = Tipo_Movimiento.objects.all()
		for t in tm:
			print(t.id)
			print(t.tipo_movimiento)

		print("termino 2 ")
		return True
	#prueba 5: aplicar refrendo: boleta acitva, pero que anteriormente estubo vencida, aplia refrendo al vencimiento de la segunda semana sin pagar.

	#Prueba 3: aplicar refrendo: boleta vencida, un dia despues de la fecha de vencimiento	
	#prueba 4: aplicar refrendo: boleta vencida, una semana despues de la fecha de vencimiento de la semana 5
	#Prueba 6: aplicar refrendo: boleta vencida, tiene comisiones pg pendientes de pago.
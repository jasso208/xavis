from django.test import TestCase
from empenos.models import *

class Refrendo_Semanal_Test(TestCase):
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
				
		"""
			TErminamos de crear catalogos
		"""
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

	###########   Comisiones PG   ##############

	#1: Se le intenta aplicar descuento a la boleta, pero esta en estatus diferente de almoneda y de remate
	def test_aplica_comisiones_a_boleta_activa(self):

		hoy = date.today()
		un_dia=timedelta(days = 1)
		tm = Tipo_Movimiento.objects.get(id = 4 )
		estatus_boleta = Estatus_Boleta.objects.get(id = 1)
		usuario = User.objects.get(username = "jasso208")

		#creamos una boleta para la prueba		
		sucursal = Sucursal.objects.get(sucursal = "prueba")

		tp = Tipo_Producto.objects.get(id = 1)
		caja = None
		
		avaluo = 0
		mutuo = 0
		fecha_vencimiento = datetime.combine(hoy + (timedelta(days = 14)),time.min)#para la prueba  no importa la fecha de vencimiento
		cliente = Cliente.objects.get(id=1)
		nombre_cotitular = "test_1"
		apellido_paterno = ""
		apellido_materno = ""
		plazo=Plazo.objects.get(id=1)
		fecha_vencimiento_real = fecha_vencimiento##para esta prueba no importa la fecha de vencimiento

		boleta = Boleta_Empeno.nuevo_empeno(sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus_boleta,3,tm)		

		abono2 = Abono()
		abono2.folio = 2
		abono2.tipo_movimiento = Tipo_Movimiento.objects.get(id = 5)
		abono2.sucursal = sucursal
		abono2.fecha = hoy
		abono2.usuario = usuario
		abono2.importe = 100
		abono2.caja = caja
		abono2.boleta = boleta
		abono2.save()

		#como la boleta esta activa, no se le puede aplicar descuento
		rcpg = boleta.fn_paga_comision_pg(10,abono2)		
		self.assertEqual(False,rcpg[0])
		self.assertEqual("No es posible aplicar descuento a la boleta.",rcpg[1])

		#Se le pasa 0 como descuento y regresa True
		rcpg = boleta.fn_paga_comision_pg(0,abono2)		
		self.assertEqual(True,rcpg[0])

	#2: la boleta lleva 3 dias vencida pero tiene 2 comisiones pg
	def test_valida_dias_vencida_vs_comisionespg_sinpagar(self):

		hoy = date.today()
		un_dia=timedelta(days = 1)
		tm = Tipo_Movimiento.objects.get(id = 4 )
		estatus_boleta = Estatus_Boleta.objects.get(id = 3)
		usuario = User.objects.get(username = "jasso208")

		#creamos una boleta para la prueba		
		sucursal = Sucursal.objects.get(sucursal = "prueba")

		tp = Tipo_Producto.objects.get(id = 1)
		caja = None
		
		avaluo = 0
		mutuo = 0
		#tiene tres dias vencida.
		fecha_vencimiento = datetime.combine(hoy - (timedelta(days = 3)),time.min)
		cliente = Cliente.objects.get(id=1)
		nombre_cotitular = "test_1"
		apellido_paterno = ""
		apellido_materno = ""
		plazo=Plazo.objects.get(id=1)
		fecha_vencimiento_real = fecha_vencimiento##para esta prueba no importa la fecha de vencimiento

		boleta = Boleta_Empeno.nuevo_empeno(sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus_boleta,3,tm)		

		abono2 = Abono()
		abono2.folio = 2
		abono2.tipo_movimiento = Tipo_Movimiento.objects.get(id = 5)
		abono2.sucursal = sucursal
		abono2.fecha = hoy
		abono2.usuario = usuario
		abono2.importe = 100
		abono2.caja = caja
		abono2.boleta = boleta
		abono2.save()

		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = datetime(2021,1,1,0,0)
		pago1.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago1.abono = abono2
		pago1.save()


		pago2 = Pagos()
		pago2.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago2.boleta = boleta
		pago2.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago2.almacenaje = 0.00
		pago2.interes = 0.00
		pago2.iva = 0.00
		pago2.importe = 12
		pago2.vencido = "N"
		pago2.pagado = "N"
		pago2.fecha_pago = datetime(2021,1,1,0,0)
		pago2.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago2.abono = abono2
		pago2.save()


		pago3 = Pagos()
		pago3.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago3.boleta = boleta
		pago3.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago3.almacenaje = 0.00
		pago3.interes = 0.00
		pago3.iva = 0.00
		pago3.importe = 12
		pago3.vencido = "N"
		pago3.pagado = "S"
		pago3.fecha_pago = datetime(2021,1,1,0,0)
		pago3.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago3.abono = abono2
		pago3.save()

		rcpg = boleta.fn_paga_comision_pg(24,abono2)		
		self.assertEqual(False,rcpg[0])
		self.assertEqual("La boleta presenta inconcistencias entre los dias vencidos y importe de comisiones pg.",rcpg[1])
	#3: La boleta tiene mas d ters dias vencida, no se le puede aplicar descuento
	def test_validamos_dias_vencida_para_descuento(self):
		hoy = date.today()
		un_dia=timedelta(days = 1)
		tm = Tipo_Movimiento.objects.get(id = 4 )
		estatus_boleta = Estatus_Boleta.objects.get(id = 3)
		usuario = User.objects.get(username = "jasso208")

		#creamos una boleta para la prueba		
		sucursal = Sucursal.objects.get(sucursal = "prueba")

		tp = Tipo_Producto.objects.get(id = 1)
		caja = None
		
		avaluo = 0
		mutuo = 0
		#tiene tres dias vencida.
		fecha_vencimiento = datetime.combine(hoy - (timedelta(days = 5)),time.min)
		cliente = Cliente.objects.get(id=1)
		nombre_cotitular = "test_1"
		apellido_paterno = ""
		apellido_materno = ""
		plazo=Plazo.objects.get(id=1)
		fecha_vencimiento_real = fecha_vencimiento##para esta prueba no importa la fecha de vencimiento

		boleta = Boleta_Empeno.nuevo_empeno(sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus_boleta,4,tm)		

		abono2 = Abono()
		abono2.folio = 2
		abono2.tipo_movimiento = Tipo_Movimiento.objects.get(id = 5)
		abono2.sucursal = sucursal
		abono2.fecha = hoy
		abono2.usuario = usuario
		abono2.importe = 100
		abono2.caja = caja
		abono2.boleta = boleta
		abono2.save()

		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = datetime(2021,1,1,0,0)
		pago1.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago1.abono = abono2
		pago1.save()

		pago2 = Pagos()
		pago2.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago2.boleta = boleta
		pago2.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago2.almacenaje = 0.00
		pago2.interes = 0.00
		pago2.iva = 0.00
		pago2.importe = 12
		pago2.vencido = "N"
		pago2.pagado = "N"
		pago2.fecha_pago = datetime(2021,1,1,0,0)
		pago2.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago2.abono = abono2
		pago2.save()

		pago3 = Pagos()
		pago3.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago3.boleta = boleta
		pago3.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago3.almacenaje = 0.00
		pago3.interes = 0.00
		pago3.iva = 0.00
		pago3.importe = 12
		pago3.vencido = "N"
		pago3.pagado = "N"
		pago3.fecha_pago = datetime(2021,1,1,0,0)
		pago3.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago3.abono = abono2
		pago3.save()

		pago4 = Pagos()
		pago4.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago4.boleta = boleta
		pago4.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago4.almacenaje = 0.00
		pago4.interes = 0.00
		pago4.iva = 0.00
		pago4.importe = 12
		pago4.vencido = "N"
		pago4.pagado = "N"
		pago2.fecha_pago = datetime(2021,1,1,0,0)
		pago2.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago4.abono = abono2
		pago4.save()

		pago5 = Pagos()
		pago5.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago5.boleta = boleta
		pago5.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago5.almacenaje = 0.00
		pago5.interes = 0.00
		pago5.iva = 0.00
		pago5.importe = 12
		pago5.vencido = "N"
		pago5.pagado = "N"
		pago5.fecha_pago = datetime(2021,1,1,0,0)
		pago5.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago5.abono = abono2
		pago5.save()

		print("empezamos validacion")
		rcpg = boleta.fn_paga_comision_pg(60,abono2)	
		cad = rcpg[1]
		self.assertEqual(False,rcpg[0])
		self.assertEqual("No es posible aplicar descuento a la boleta. Tiene mas de tres dias vencida.",cad)
	#4: validamos que el importe de descuento cubra al 100% las comisiones pg
	def test_valida_importe_destinado_a_descuento(self):
		hoy = date.today()
		un_dia=timedelta(days = 1)
		tm = Tipo_Movimiento.objects.get(id = 4 )
		estatus_boleta = Estatus_Boleta.objects.get(id = 3)
		usuario = User.objects.get(username = "jasso208")

		#creamos una boleta para la prueba		
		sucursal = Sucursal.objects.get(sucursal = "prueba")

		tp = Tipo_Producto.objects.get(id = 1)
		caja = None
		
		avaluo = 0
		mutuo = 0
		#tiene tres dias vencida.
		fecha_vencimiento = datetime.combine(hoy - (timedelta(days = 3)),time.min)
		cliente = Cliente.objects.get(id=1)
		nombre_cotitular = "test_1"
		apellido_paterno = ""
		apellido_materno = ""
		plazo=Plazo.objects.get(id=1)
		fecha_vencimiento_real = fecha_vencimiento##para esta prueba no importa la fecha de vencimiento

		boleta = Boleta_Empeno.nuevo_empeno(sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus_boleta,3,tm)		

		abono2 = Abono()
		abono2.folio = 2
		abono2.tipo_movimiento = Tipo_Movimiento.objects.get(id = 5)
		abono2.sucursal = sucursal
		abono2.fecha = hoy
		abono2.usuario = usuario
		abono2.importe = 100
		abono2.caja = caja
		abono2.boleta = boleta
		abono2.save()

		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = datetime(2021,1,1,0,0)
		pago1.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago1.abono = abono2
		pago1.save()


		pago2 = Pagos()
		pago2.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago2.boleta = boleta
		pago2.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago2.almacenaje = 0.00
		pago2.interes = 0.00
		pago2.iva = 0.00
		pago2.importe = 12
		pago2.vencido = "N"
		pago2.pagado = "N"
		pago2.fecha_pago = datetime(2021,1,1,0,0)
		pago2.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago2.abono = abono2
		pago2.save()


		pago3 = Pagos()
		pago3.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago3.boleta = boleta
		pago3.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago3.almacenaje = 0.00
		pago3.interes = 0.00
		pago3.iva = 0.00
		pago3.importe = 12
		pago3.vencido = "N"
		pago3.pagado = "N"
		pago3.fecha_pago = datetime(2021,1,1,0,0)
		pago3.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago3.abono = abono2
		pago3.save()

		rcpg = boleta.fn_paga_comision_pg(24,abono2)		
		self.assertEqual(False,rcpg[0])
		self.assertEqual("El importe a descontar no cubre las comisiones de periodo de gracia.",rcpg[1])

	#5 Aplicamos descuento correctamente
	def test_aplicamos_descuento(self):
		hoy = date.today()
		un_dia=timedelta(days = 1)
		tm = Tipo_Movimiento.objects.get(id = 4 )
		estatus_boleta = Estatus_Boleta.objects.get(id = 3)
		usuario = User.objects.get(username = "jasso208")

		#creamos una boleta para la prueba		
		sucursal = Sucursal.objects.get(sucursal = "prueba")

		tp = Tipo_Producto.objects.get(id = 1)
		caja = None
		
		avaluo = 0
		mutuo = 0
		#tiene tres dias vencida.
		fecha_vencimiento = datetime.combine(hoy - (timedelta(days = 3)),time.min)
		cliente = Cliente.objects.get(id=1)
		nombre_cotitular = "test_1"
		apellido_paterno = ""
		apellido_materno = ""
		plazo=Plazo.objects.get(id=1)
		fecha_vencimiento_real = fecha_vencimiento##para esta prueba no importa la fecha de vencimiento

		boleta = Boleta_Empeno.nuevo_empeno(sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus_boleta,3,tm)		

		abono2 = Abono()
		abono2.folio = 2
		abono2.tipo_movimiento = Tipo_Movimiento.objects.get(id = 5)
		abono2.sucursal = sucursal
		abono2.fecha = hoy
		abono2.usuario = usuario
		abono2.importe = 100
		abono2.caja = caja
		abono2.boleta = boleta
		abono2.save()

		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = datetime(2021,1,1,0,0)
		pago1.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago1.abono = abono2
		pago1.save()


		pago2 = Pagos()
		pago2.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago2.boleta = boleta
		pago2.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago2.almacenaje = 0.00
		pago2.interes = 0.00
		pago2.iva = 0.00
		pago2.importe = 12
		pago2.vencido = "N"
		pago2.pagado = "N"
		pago2.fecha_pago = datetime(2021,1,1,0,0)
		pago2.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago2.abono = abono2
		pago2.save()


		pago3 = Pagos()
		pago3.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago3.boleta = boleta
		pago3.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago3.almacenaje = 0.00
		pago3.interes = 0.00
		pago3.iva = 0.00
		pago3.importe = 12
		pago3.vencido = "N"
		pago3.pagado = "N"
		pago3.fecha_pago = datetime(2021,1,1,0,0)
		pago3.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago3.abono = abono2
		pago3.save()

		pago4 = Pagos()
		pago4.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago4.boleta = boleta
		pago4.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago4.almacenaje = 0.00
		pago4.interes = 0.00
		pago4.iva = 0.00
		pago4.importe = 12
		pago4.vencido = "N"
		pago4.pagado = "N"
		pago4.fecha_pago = datetime(2021,1,1,0,0)
		pago4.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago4.abono = abono2
		pago4.save()		

		Pagos_Com_Pg_No_Usados.objects.all().delete()
		rcpg = boleta.fn_paga_comision_pg(36,abono2)		
		self.assertEqual(True,rcpg[0])
		#validamos que las tres comisiones pg se hayan respaldado.
		self.assertEqual(3,Pagos_Com_Pg_No_Usados.objects.all().count())
		#Validamos que las tres comisioens pg ya no existan

		self.assertEqual(0,Pagos.objects.filter(boleta = boleta,pagado = "S",tipo_pago__id = 2).count())

	#6 pagamos las comisiones pg, NO se aplica descuento
	def test_pagamos_comisionespg(self):
		hoy = date.today()
		un_dia=timedelta(days = 1)
		tm = Tipo_Movimiento.objects.get(id = 4 )
		estatus_boleta = Estatus_Boleta.objects.get(id = 3)
		usuario = User.objects.get(username = "jasso208")

		#creamos una boleta para la prueba		
		sucursal = Sucursal.objects.get(sucursal = "prueba")

		tp = Tipo_Producto.objects.get(id = 1)
		caja = None
		
		avaluo = 0
		mutuo = 0
		#tiene tres dias vencida.
		fecha_vencimiento = datetime.combine(hoy - (timedelta(days = 3)),time.min)
		cliente = Cliente.objects.get(id=1)
		nombre_cotitular = "test_1"
		apellido_paterno = ""
		apellido_materno = ""
		plazo=Plazo.objects.get(id=1)
		fecha_vencimiento_real = fecha_vencimiento##para esta prueba no importa la fecha de vencimiento

		boleta = Boleta_Empeno.nuevo_empeno(sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus_boleta,3,tm)		

		abono2 = Abono()
		abono2.folio = 2
		abono2.tipo_movimiento = Tipo_Movimiento.objects.get(id = 5)
		abono2.sucursal = sucursal
		abono2.fecha = hoy
		abono2.usuario = usuario
		abono2.importe = 100
		abono2.caja = caja
		abono2.boleta = boleta
		abono2.save()

		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = datetime(2021,1,1,0,0)
		pago1.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago1.abono = abono2
		pago1.save()


		pago2 = Pagos()
		pago2.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago2.boleta = boleta
		pago2.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago2.almacenaje = 0.00
		pago2.interes = 0.00
		pago2.iva = 0.00
		pago2.importe = 12
		pago2.vencido = "N"
		pago2.pagado = "N"
		pago2.fecha_pago = datetime(2021,1,1,0,0)
		pago2.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago2.abono = abono2
		pago2.save()


		pago3 = Pagos()
		pago3.tipo_pago = Tipo_Pago.objects.get(id = 2)
		pago3.boleta = boleta
		pago3.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago3.almacenaje = 0.00
		pago3.interes = 0.00
		pago3.iva = 0.00
		pago3.importe = 12
		pago3.vencido = "N"
		pago3.pagado = "N"
		pago3.fecha_pago = datetime(2021,1,1,0,0)
		pago3.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago3.abono = abono2
		pago3.save()

		pago4 = Pagos()
		pago4.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago4.boleta = boleta
		pago4.fecha_vencimiento = datetime(2021,1,1,0,0)
		pago4.almacenaje = 0.00
		pago4.interes = 0.00
		pago4.iva = 0.00
		pago4.importe = 12
		pago4.vencido = "N"
		pago4.pagado = "N"
		pago4.fecha_pago = datetime(2021,1,1,0,0)
		pago4.fecha_vencimiento_real = datetime(2021,1,1,0,0)
		pago4.abono = abono2
		pago4.save()

		Pagos_Com_Pg_No_Usados.objects.all().delete()
		rcpg = boleta.fn_paga_comision_pg(0,abono2)		
		self.assertEqual(True,rcpg[0])
		#Validamos que no se haya respaldado nada
		self.assertEqual(0,Pagos_Com_Pg_No_Usados.objects.all().count())

		#Validamos que las tres comisioens pg esten pagadas

		self.assertEqual(3,Pagos.objects.filter(boleta = boleta,pagado = "S",tipo_pago__id = 2).count())


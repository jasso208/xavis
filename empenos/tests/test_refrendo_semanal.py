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
		self.assertEqual("La boleta presenta inconcistencias entre los dias vencidos y el importe de comisiones pg.",rcpg[1])
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


	#####   Se aplican pagos ####

	#1: No debe contar con comiion pg pendientes de pago
	#ya que o se aplico descuento o se pagaron previamente.
	def test_validamos_no_tenga_comisionpg(self):
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

		abono = Abono()
		abono.folio = 2
		abono.tipo_movimiento = Tipo_Movimiento.objects.get(id = 5)
		abono.sucursal = sucursal
		abono.fecha = hoy
		abono.usuario = usuario
		abono.importe = 100
		abono.caja = caja
		abono.boleta = boleta
		abono.save()


		#creamos una comision pg
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
		pago1.abono = abono
		pago1.save()


		respuesta = boleta.fn_salda_pagos(1,100,abono)

		self.assertEqual(respuesta[0],False)
		self.assertEqual(respuesta[1],"Error al pagar las semanas indicadas. No se liquidaron correctamente las comisiones de periodo de gracia.")

	#2: En los pagos que estan por cubrir, su fecha de vencimiento y fecha vencimiento real no debe tener diferencia mayor a 2 dias
	#si puede presentarse este esenario pero seria muy extraño.
	def test_validamos_fechavencimiento_vs_fechavencimientoreal_de_pago(self):
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

			abono = Abono()
			abono.folio = 2
			abono.tipo_movimiento = Tipo_Movimiento.objects.get(id = 5)
			abono.sucursal = sucursal
			abono.fecha = hoy
			abono.usuario = usuario
			abono.importe = 100
			abono.caja = caja
			abono.boleta = boleta
			abono.save()

			
			
			pago1 = Pagos()
			pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
			pago1.boleta = boleta
			pago1.fecha_vencimiento = datetime(2021,1,30,0,0)
			pago1.almacenaje = 0.00
			pago1.interes = 0.00
			pago1.iva = 0.00
			pago1.importe = 12
			pago1.vencido = "N"
			pago1.pagado = "N"
			pago1.fecha_pago = None
			pago1.fecha_vencimiento_real = datetime(2021,1,30,0,0)
			pago1.abono = abono
			pago1.save()


			pago1 = Pagos()
			pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
			pago1.boleta = boleta
			pago1.fecha_vencimiento = datetime(2021,2,6,0,0)
			pago1.almacenaje = 0.00
			pago1.interes = 0.00
			pago1.iva = 0.00
			pago1.importe = 12
			pago1.vencido = "N"
			pago1.pagado = "N"
			pago1.fecha_pago = None
			pago1.fecha_vencimiento_real = datetime(2021,2,6,0,0)
			pago1.abono = abono
			pago1.save()


			pago1 = Pagos()
			pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
			pago1.boleta = boleta
			pago1.fecha_vencimiento = datetime(2021,2,13,0,0)
			pago1.almacenaje = 0.00
			pago1.interes = 0.00
			pago1.iva = 0.00
			pago1.importe = 12
			pago1.vencido = "N"
			pago1.pagado = "N"
			pago1.fecha_pago = None
			pago1.fecha_vencimiento_real = datetime(2021,2,13,0,0)
			pago1.abono = abono
			pago1.save()


			pago1 = Pagos()
			pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
			pago1.boleta = boleta
			pago1.fecha_vencimiento = datetime(2021,2,20,0,0)
			pago1.almacenaje = 0.00
			pago1.interes = 0.00
			pago1.iva = 0.00
			pago1.importe = 12
			pago1.vencido = "N"
			pago1.pagado = "N"
			pago1.fecha_pago = None
			pago1.fecha_vencimiento_real = datetime(2021,2,18,0,0)
			pago1.abono = abono
			pago1.save()


			respuesta = boleta.fn_salda_pagos(1,100,abono)

			self.assertEqual(respuesta[0],False)
			self.assertEqual(respuesta[1],"Error al pagar las semanas indicadas. La fecha de vencimiento es diferente a la fecha de vencimiento real.")


	#3: en la boleta a la que pertenecen los pagos no la fecha de vencimiento y fecha vencimiento real no debe tener difrencia mayor a 2 dias
	#este esenario si puede presentarse, pero seria muy extraño.
	def test_validamos_fechavencimiento_vs_fechavencimientoreal_de_boleta(self):
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

		abono = Abono()
		abono.folio = 2
		abono.tipo_movimiento = Tipo_Movimiento.objects.get(id = 5)
		abono.sucursal = sucursal
		abono.fecha = hoy
		abono.usuario = usuario
		abono.importe = 100
		abono.caja = caja
		abono.boleta = boleta
		abono.save()

		
		
		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime(2021,1,30,0,0)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime(2021,1,30,0,0)
		pago1.abono = abono
		pago1.save()


		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime(2021,2,6,0,0)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime(2021,2,6,0,0)
		pago1.abono = abono
		pago1.save()


		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime(2021,2,13,0,0)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime(2021,2,13,0,0)
		pago1.abono = abono
		pago1.save()

		boleta.fecha_vencimiento = datetime(2021,2,13,0,0)
		boleta.fecha_vencimiento_real = datetime(2021,2,11,0,0)
		boleta.save()

		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime(2021,2,20,0,0)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime(2021,2,20,0,0)
		pago1.abono = abono
		pago1.save()


		respuesta = boleta.fn_salda_pagos(1,100,abono)

		self.assertEqual(respuesta[0],False)
		self.assertEqual(respuesta[1],"Error al pagar las semanas indicadas. La fecha de vencimiento de la boleta es diferente a la fecha de vencimiento real.")


	#4:	#el numero de pagos a liquidar debe ser mayor o igul al minimo de pagos o menor o igual al maximo de pagos.

	def test_validamos_semanas_a_pagar_1(self):
		hoy = date.today()
		hoy = datetime.combine(hoy,time.min)
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
		fecha_vencimiento = datetime.combine(hoy + (timedelta(days = 28)),time.min)#para la prueba  no importa la fecha de vencimiento
		cliente = Cliente.objects.get(id=1)
		nombre_cotitular = "test_1"
		apellido_paterno = ""
		apellido_materno = ""
		plazo=Plazo.objects.get(id=1)
		fecha_vencimiento_real = fecha_vencimiento##para esta prueba no importa la fecha de vencimiento

		boleta = Boleta_Empeno.nuevo_empeno(sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus_boleta,3,tm)		

		abono = Abono()
		abono.folio = 2
		abono.tipo_movimiento = Tipo_Movimiento.objects.get(id = 5)
		abono.sucursal = sucursal
		abono.fecha = hoy
		abono.usuario = usuario
		abono.importe = 100
		abono.caja = caja
		abono.boleta = boleta
		abono.save()

		
		
		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy + timedelta(days = 7),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy + timedelta(days = 7),time.min)
		pago1.abono = abono
		pago1.save()


		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy + timedelta(days = 14),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy + timedelta(days = 14),time.min)
		pago1.abono = abono
		pago1.save()


		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy + timedelta(days = 21),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy + timedelta(days = 21),time.min)
		pago1.abono = abono
		pago1.save()

		boleta.fecha_vencimiento = datetime.combine(hoy + timedelta(days = 28),time.min)
		boleta.fecha_vencimiento_real = datetime.combine(hoy + timedelta(days = 28),time.min)
		boleta.save()

		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy + timedelta(days = 28),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy + timedelta(days = 28),time.min)
		pago1.abono = abono
		pago1.save()

		#print("antes del pago")
		#pagos = Pagos.objects.filter(boleta = boleta).order_by("fecha_vencimiento")
		#for p in pagos:
		#	print(p.fecha_vencimiento)
		#print(boleta.fn_get_min_y_max_semanas_a_pagar())

		#como estamos abonando el dia en que se dio de alta la boleta, si lo permite
		respuesta = boleta.fn_salda_pagos(1,100,abono)

		#print("despues del pago")
		#pagos = Pagos.objects.filter(boleta = boleta).order_by("fecha_vencimiento")
		#for p in pagos:
		#	print(p.fecha_vencimiento)
		#print(boleta.fn_get_min_y_max_semanas_a_pagar())


		#este abono ya no lo permite
		respuesta = boleta.fn_salda_pagos(1,100,abono)

		self.assertEqual(respuesta[0],False)
		self.assertEqual(respuesta[1],"Error al pagar las semanas indicadas. El numero maximo de semanas a pagar es cero.")



	def test_validamos_semanas_a_pagar_2(self):
		hoy = date.today()
		hoy = datetime.combine(hoy,time.min)
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

		abono = Abono()
		abono.folio = 2
		abono.tipo_movimiento = Tipo_Movimiento.objects.get(id = 5)
		abono.sucursal = sucursal
		abono.fecha = hoy
		abono.usuario = usuario
		abono.importe = 100
		abono.caja = caja
		abono.boleta = boleta
		abono.save()

		
		
		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy - timedelta(days = 7),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 10
		pago1.vencido = "S"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy - timedelta(days = 7),time.min)
		pago1.abono = abono
		pago1.save()


		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy,time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 10
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy,time.min)
		pago1.abono = abono
		pago1.save()


		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy + timedelta(days = 7),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 10
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy + timedelta(days = 7),time.min)
		pago1.abono = abono
		pago1.save()

		boleta.fecha_vencimiento = datetime.combine(hoy + timedelta(days = 14),time.min)
		boleta.fecha_vencimiento_real = datetime.combine(hoy + timedelta(days = 14),time.min)
		boleta.save()

		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy + timedelta(days = 14),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 10
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy + timedelta(days = 14),time.min)
		pago1.abono = abono
		pago1.save()

		#pagos = Pagos.objects.filter(boleta = boleta).order_by("fecha_vencimiento")
		#for p in pagos:
		#	print(p.fecha_vencimiento)

		#print(boleta.fn_get_min_y_max_semanas_a_pagar())

		respuesta = boleta.fn_salda_pagos(3,100,abono)

		self.assertEqual(respuesta[0],False)
		self.assertEqual(respuesta[1],"Error al pagar las semanas indicadas. El numero de semanas a pagar no es correcto.")


	#5: #El import a pagos debe cubrir al 100% el saldo del numero de pagos
	def test_validamos_importe_a_pagos(self):
		hoy = date.today()
		hoy = datetime.combine(hoy,time.min)
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

		abono = Abono()
		abono.folio = 2
		abono.tipo_movimiento = Tipo_Movimiento.objects.get(id = 5)
		abono.sucursal = sucursal
		abono.fecha = hoy
		abono.usuario = usuario
		abono.importe = 100
		abono.caja = caja
		abono.boleta = boleta
		abono.save()

		
		
		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy - timedelta(days = 7),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "S"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy - timedelta(days = 7),time.min)
		pago1.abono = abono
		pago1.save()


		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy,time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy,time.min)
		pago1.abono = abono
		pago1.save()


		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy + timedelta(days = 7),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy + timedelta(days = 7),time.min)
		pago1.abono = abono
		pago1.save()

		boleta.fecha_vencimiento = datetime.combine(hoy + timedelta(days = 14),time.min)
		boleta.fecha_vencimiento_real = datetime.combine(hoy + timedelta(days = 14),time.min)
		boleta.save()

		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy + timedelta(days = 14),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy + timedelta(days = 14),time.min)
		pago1.abono = abono
		pago1.save()

		#pagos = Pagos.objects.filter(boleta = boleta).order_by("fecha_vencimiento")
		#for p in pagos:
		#	print(p.fecha_vencimiento)

		#print(boleta.fn_get_min_y_max_semanas_a_pagar())

		respuesta = boleta.fn_salda_pagos(2,23,abono)

		self.assertEqual(respuesta[0],False)
		self.assertEqual(respuesta[1],"Error al pagar las semanas indicadas. El importe destinado a refrendos no cubre el numero de semanas indicadas.")

	#6: #cuando el abono se aplica correctamente, no deben existir refrendos pg sin pagar.
	def test_abono_correcto_no_debe_existir_refrendopg(self):
		hoy = date.today()
		hoy = datetime.combine(hoy,time.min)
		un_dia=timedelta(days = 1)
		tm = Tipo_Movimiento.objects.get(id = 4 )
		estatus_boleta = Estatus_Boleta.objects.get( id = 3 )
		usuario = User.objects.get(username = "jasso208")

		#creamos una boleta vencida para la prueba		
		#la boleta vencio ayer
		sucursal = Sucursal.objects.get(sucursal = "prueba")

		tp = Tipo_Producto.objects.get(id = 1)
		caja = None
		
		avaluo = 0
		mutuo = 0
		fecha_vencimiento = datetime.combine(hoy - (timedelta(days = 1)),time.min)#para la prueba  no importa la fecha de vencimiento
		cliente = Cliente.objects.get(id=1)
		nombre_cotitular = "test_1"
		apellido_paterno = ""
		apellido_materno = ""
		plazo=Plazo.objects.get(id=1)
		fecha_vencimiento_real = fecha_vencimiento

		boleta = Boleta_Empeno.nuevo_empeno(sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus_boleta,3,tm)		

		abono = Abono()
		abono.folio = 2
		abono.tipo_movimiento = Tipo_Movimiento.objects.get(id = 5)
		abono.sucursal = sucursal
		abono.fecha = hoy
		abono.usuario = usuario
		abono.importe = 100
		abono.caja = caja
		abono.boleta = boleta
		abono.save()

		
		
		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy - timedelta(days = 29),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "S"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy - timedelta(days = 29),time.min)
		pago1.abono = abono
		pago1.save()


		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy - timedelta(days = 22),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "S"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy - timedelta(days = 22),time.min)
		pago1.abono = abono
		pago1.save()


		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy - timedelta(days = 15),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "S"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy - timedelta(days = 15),time.min)
		pago1.abono = abono
		pago1.save()

		boleta.fecha_vencimiento = datetime.combine(hoy - timedelta(days = 8),time.min)
		boleta.fecha_vencimiento_real = datetime.combine(hoy - timedelta(days = 8),time.min)
		boleta.save()

		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 1)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy - timedelta(days = 8),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "S"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy - timedelta(days = 8),time.min)
		pago1.abono = abono
		pago1.save()

		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 3)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy - timedelta(days = 1),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "S"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy - timedelta(days = 1),time.min)
		pago1.abono = abono
		pago1.save()


		pago1 = Pagos()
		pago1.tipo_pago = Tipo_Pago.objects.get(id = 3)
		pago1.boleta = boleta
		pago1.fecha_vencimiento = datetime.combine(hoy + timedelta(days = 6),time.min)
		pago1.almacenaje = 0.00
		pago1.interes = 0.00
		pago1.iva = 0.00
		pago1.importe = 12
		pago1.vencido = "N"
		pago1.pagado = "N"
		pago1.fecha_pago = None
		pago1.fecha_vencimiento_real = datetime.combine(hoy + timedelta(days = 6),time.min)
		pago1.abono = abono
		pago1.save()

		#pagos = Pagos.objects.filter(boleta = boleta).order_by("fecha_vencimiento")		

		#for p in pagos:
		#	print(p.fecha_vencimiento)

		#print(boleta.fn_get_min_y_max_semanas_a_pagar())

		respuesta = boleta.fn_salda_pagos(2,24,abono)

		#print("despues de pagar")

		#pagos = Pagos.objects.filter(boleta = boleta).order_by("fecha_vencimiento")		

		#for p in pagos:
		#	print(p.fecha_vencimiento)

		#print(boleta.fn_get_min_y_max_semanas_a_pagar())

		self.assertEqual(respuesta[0],True)

		#self.assertEqual(respuesta[1],"Error al pagar las semanas indicadas. El importe destinado a refrendos no cubre el numero de semanas indicadas.")







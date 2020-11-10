from django.test import TestCase
from empenos.jobs import *

from empenos.models import *
from datetime import date, datetime, time,timedelta
# Create your tests here.




#probamos el job para liberar los apartados que se vencen y no ha sido cubierto su saldo restante
class TestJobApartado(TestCase):
	#aqui se inicializan los valores de la prueba, se inicializa para cada prueba
	@classmethod
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


class TestConceptosRetiros(TestCase):
	@classmethod
	def setUpTestData(cls):
		Sucursal.objects.create(sucursal = "Sucursal de prueba")

		User.objects.create(username = "jasso208")

		Tipo_Movimiento.objects.create(tipo_movimiento="AP Caja",naturaleza='')
		Tipo_Movimiento.objects.create(tipo_movimiento="O I",naturaleza='')
		Tipo_Movimiento.objects.create(tipo_movimiento="Retiro Efectivo",naturaleza='')
		return True

	def test_nuevo_concepto(self):
		concepto_correcto = Concepto_Retiro.fn_nuevo_concepto(1,1,100,"concepto de prueba")
		#falla debido a la longitud del campo
		concepto_no_correcto = Concepto_Retiro.fn_nuevo_concepto(1,1,100,"concepto de prueba 1212121212121212121212")
		#no puede contener importe maximo de retiro negativo
		concepto_no_correcto_por_importe = Concepto_Retiro.fn_nuevo_concepto(1,1,-1,"concepto de prueba")		

		#no puede contener importe maximo igual a cero
		concepto_no_correcto_por_importe_cero = Concepto_Retiro.fn_nuevo_concepto(1,1,0,"concepto de prueba maximo cero")		

		concepto_usr_no_correcto = Concepto_Retiro.fn_nuevo_concepto(1,3,100,"concepto de prueba")		
		concepto_suc_no_correcta = Concepto_Retiro.fn_nuevo_concepto(3,1,100,"concepto de prueba")		
		concepto_no_concepto = Concepto_Retiro.fn_nuevo_concepto(3,1,100,"")	

		self.assertEqual(concepto_correcto,True)
		self.assertEqual(concepto_no_correcto,False)
		self.assertEqual(concepto_no_correcto_por_importe,False)
		self.assertEqual(concepto_usr_no_correcto,False)
		self.assertEqual(concepto_suc_no_correcta,False)
		self.assertEqual(concepto_no_concepto,False)
		self.assertEqual(concepto_no_correcto_por_importe_cero,False)


	def test_elimina_concepto(self):
		concepto_correcto = Concepto_Retiro.fn_nuevo_concepto(1,1,100,"prueba_elimina_concepto")
		
		concepto = Concepto_Retiro.objects.get(concepto="prueba_elimina_concepto".upper())
		User.objects.create(username = "jasso20800")
		usuario = User.objects.get(username = "jasso20800")
		resp = Concepto_Retiro.fn_delete_concepto(concepto.id,usuario.id)

		self.assertEqual(resp,True)

	def test_update_importe_maximo_retiro(self):
		concepto_correcto = Concepto_Retiro.fn_nuevo_concepto(1,1,100,"prueba_update_retiro")
		concepto_correcto_2 = Concepto_Retiro.fn_nuevo_concepto(1,1,100,"prueba_update_retiro_negativo")
		concepto_correcto_3 = Concepto_Retiro.fn_nuevo_concepto(1,1,100,"prueba_update_retiro_cero")
		

		concepto = Concepto_Retiro.objects.get(concepto = "prueba_update_retiro".upper())
		concepto_2 = Concepto_Retiro.objects.get(concepto = "prueba_update_retiro_negativo".upper())
		concepto_3 = Concepto_Retiro.objects.get(concepto = "prueba_update_retiro_cero".upper())

		User.objects.create(username = "jasso_update")
		usuario = User.objects.get(username = "jasso_update")
	
		resp = Concepto_Retiro.fn_update_importe_maximo_retiro(concepto.id,200,usuario.id)
		
		resp_2 = Concepto_Retiro.fn_update_importe_maximo_retiro(concepto_2.id,-200,usuario.id)

		resp_3 = Concepto_Retiro.fn_update_importe_maximo_retiro(concepto_2.id,0,usuario.id)
		
		concepto = Concepto_Retiro.objects.get(concepto = "prueba_update_retiro".upper())

		self.assertEqual(decimal.Decimal(concepto.importe_maximo_retiro),decimal.Decimal(200))
		self.assertEqual(resp,True)		
		self.assertEqual(resp_2,False)
		self.assertEqual(resp_3,False)

	#prueba para consultar el saldo de un concepto de retiro.
	def test_saldo_concepto(self):
		nuevo_concepto = Concepto_Retiro.fn_nuevo_concepto(1,1,100,"nvo_concepto")
		segundo_concepto = Concepto_Retiro.fn_nuevo_concepto(1,1,100,"segundo_concepto")
		tercer_concepto = Concepto_Retiro.fn_nuevo_concepto(1,1,150,"tercer_concepto")

		#probamos el saldo de un concepto cuando aun no se hacen retiros.		
		concepto_nvo_concepto = Concepto_Retiro.objects.get(concepto="nvo_concepto".upper())
		saldo = concepto_nvo_concepto.fn_saldo_concepto()

		#probams el saldo haciendo un retiro
		tm_retiro_efectivo = Tipo_Movimiento.objects.get(id=3)
		sucursal = Sucursal.objects.get(sucursal = "Sucursal de prueba")
		usuario = User.objects.get(username = "jasso208")
		concepto_segundo_concepto = Concepto_Retiro.objects.get(concepto="segundo_concepto".upper())
		Retiro_Efectivo.objects.create(folio = 1,tipo_movimiento = tm_retiro_efectivo,sucursal = sucursal, usuario = usuario, importe = 50,concepto = concepto_segundo_concepto, token = 10)
		saldo_segundo_concepto = concepto_segundo_concepto.fn_saldo_concepto()

		#probamos el saldo retirando al 100% el concepto
		tm_retiro_efectivo = Tipo_Movimiento.objects.get(id=3)
		sucursal = Sucursal.objects.get(sucursal = "Sucursal de prueba")
		usuario = User.objects.get(username = "jasso208")
		concepto_tercer_concepto = Concepto_Retiro.objects.get(concepto="tercer_concepto".upper())
		Retiro_Efectivo.objects.create(folio = 1,tipo_movimiento = tm_retiro_efectivo,sucursal = sucursal, usuario = usuario, importe = 150,concepto = concepto_tercer_concepto, token = 10)
		saldo_tercer_concepto = concepto_tercer_concepto.fn_saldo_concepto()


		self.assertEqual(saldo,100)
		self.assertEqual(saldo_segundo_concepto,50)
		self.assertEqual(saldo_tercer_concepto,0)


class TestRetiros(TestCase):

	@classmethod
	def setUpTestData(cls):
		Sucursal.objects.create(sucursal = "Sucursal de prueba")

		User.objects.create(username = "jasso208")

		Tipo_Movimiento.objects.create(tipo_movimiento="AP Caja",naturaleza='')
		Tipo_Movimiento.objects.create(tipo_movimiento="O I",naturaleza='')
		Tipo_Movimiento.objects.create(tipo_movimiento="Retiro Efectivo",naturaleza='')

		return True

	def test_cancela_retiro(self):

		sucursal = Sucursal.objects.get(sucursal = "Sucursal de prueba")
		usuario = User.objects.get(username = "jasso208")
		nuevo_concepto = Concepto_Retiro.fn_nuevo_concepto(sucursal.id,usuario.id,100,"nvo_concepto")
		segundo_concepto = Concepto_Retiro.fn_nuevo_concepto(sucursal.id,usuario.id,100,"segundo_concepto")
		tercer_concepto = Concepto_Retiro.fn_nuevo_concepto(sucursal.id,usuario.id,150,"tercer_concepto")
		tm_retiro_efectivo = Tipo_Movimiento.objects.get(tipo_movimiento="Retiro Efectivo")	
		concepto_segundo_concepto = Concepto_Retiro.objects.get(concepto="segundo_concepto".upper())



		#creamos un retiro
		Retiro_Efectivo.objects.create(folio = 1,tipo_movimiento = tm_retiro_efectivo,sucursal = sucursal, usuario = usuario, importe = 50,concepto = concepto_segundo_concepto, token = 10)
		
		retiro_1 = Retiro_Efectivo.objects.get(folio = 1, sucursal = sucursal)		

		#obtenemos el saldo del concepto despues de haber realizado el retiro
		saldo_antes_cancelar = concepto_segundo_concepto.fn_saldo_concepto()

		#cancelamos el retiro
		retiro_1.fn_cancela_retiro(usuario.id,"cancelacion_retiro")

		#obtenemos el saldo despues de haber cancelado el retiro
		saldo_despues_cancela = concepto_segundo_concepto.fn_saldo_concepto()

		self.assertEqual(saldo_antes_cancelar,50)#cuando se hiso el retiro, se quedo con saldo de 50 pesos
		self.assertEqual(retiro_1.comentario,'cancelacion_retiro')#cuando se cancelo el retiro se le paso el comentario "cancelacion_retiro"
		self.assertEqual(retiro_1.importe,0)#cuando se cancelo el retiro, se queda con importe 0
		self.assertEqual(saldo_despues_cancela,100)#el saldo del concepto despues de haber cancelado  el retiro vuelve a ser 100
		self.assertEqual(retiro_1.usuario_cancela,usuario)#almacenamos tambien el usuario que cancela.
		self.assertEqual(retiro_1.activo,2)## el status del retiro es cancelado


class TestSucursales(TestCase):

	#aqui inicializamos valores para la prueba
	@classmethod
	def setUpTestData(cls):
		Sucursal.objects.create(sucursal = "Sucursal de prueba")
		Sucursal.objects.create(sucursal = "Sucursal de prueba 2")

		Sucursal.objects.create(sucursal = "Sucursal de prueba 3")

		User.objects.create(username = "jasso208")

	def test_fn_consulta_porcentaje_mutuo(self):
		sucursal = Sucursal.objects.get(sucursal = "Sucursal de prueba" )
		sucursal2 = Sucursal.objects.get(sucursal = "Sucursal de prueba 2" )

		resp_1 = sucursal.fn_consulta_porcentaje_mutuo()		
		resp_2 = sucursal.fn_actualiza_porcentaje_mutuo(1,2,3)
		resp_3 = sucursal.fn_consulta_porcentaje_mutuo()
		resp_4 = sucursal2.fn_consulta_porcentaje_mutuo()		
		sucursal.fn_actualiza_porcentaje_mutuo(4,5,6)
		resp_5 = sucursal.fn_consulta_porcentaje_mutuo()
		
		

		#esta debe fallar ya que se consulto antes de que se generara la configuracion de porcentajes mutuos.
		self.assertEqual(type(resp_1),type(False))
		#se debe actualizar correctamente los parametros de configuracion
		self.assertEqual(resp_2,True)
		#como se consulto despues de haber creado la configuracion de porcentaje de mutuo, no debe ser false
		self.assertNotEqual(type(resp_3),type(False))
		#validamos que nos regrese los valores correctos
		self.assertEqual(resp_3.porcentaje_oro,1)
		self.assertEqual(resp_3.porcentaje_plata,2)
		self.assertEqual(resp_3.porcentaje_articulos_varios,3)

		#para la sucursal 2 no hemos creado los parametros de consulta, por lo tanto debe fallar
		self.assertEqual(type(resp_4),type(False))

		#actualizamos los valores de la primera sucursal
		self.assertEqual(resp_5.porcentaje_oro,4)
		self.assertEqual(resp_5.porcentaje_plata,5)
		self.assertEqual(resp_5.porcentaje_articulos_varios,6)


	def test_fn_actualiza_porcentaje_mutuo(self):
		sucursal = Sucursal.objects.get(sucursal = "Sucursal de prueba" )
		sucursal2 = Sucursal.objects.get(sucursal = "Sucursal de prueba 2" )

		resp = sucursal.fn_actualiza_porcentaje_mutuo(1,2,3)
		resp_2 = sucursal.fn_actualiza_porcentaje_mutuo(4,5,6)

		resp_3 = sucursal.fn_actualiza_porcentaje_mutuo(4.3,5,6)
		resp_4 = sucursal.fn_actualiza_porcentaje_mutuo(4,5.5,6)
		resp_5 = sucursal.fn_actualiza_porcentaje_mutuo(4,5,6.6)
		resp_6 = sucursal.fn_actualiza_porcentaje_mutuo(1,2,3)

		resp_7 = sucursal.fn_actualiza_porcentaje_mutuo(0,5,6)
		resp_8 = sucursal.fn_actualiza_porcentaje_mutuo(1,0,6)
		resp_9 = sucursal.fn_actualiza_porcentaje_mutuo(1,2,0)

		resp_10 = sucursal.fn_consulta_porcentaje_mutuo()
		resp_11 = sucursal2.fn_consulta_porcentaje_mutuo()

		self.assertEqual(resp,True)
		self.assertEqual(resp_2,True)
		self.assertEqual(resp_3,False)
		self.assertEqual(resp_4,False)
		self.assertEqual(resp_5,False)
		self.assertEqual(resp_6,True)
		self.assertEqual(resp_7,False)
		self.assertEqual(resp_8,False)
		self.assertEqual(resp_9,False)


		self.assertEqual(resp_10.porcentaje_oro,1)
		self.assertEqual(resp_10.porcentaje_plata,2)
		self.assertEqual(resp_10.porcentaje_articulos_varios,3)
		
		self.assertEqual(resp_11,False)

	def test_fn_calcula_refrendo(self):

		sucursal = Sucursal.objects.get(sucursal = "Sucursal de prueba" )
		sucursal2 = Sucursal.objects.get(sucursal = "Sucursal de prueba 2" )
		sucursal3 = Sucursal.objects.get(sucursal = "Sucursal de prueba 3" )

		usuario = User.objects.get(username = "jasso208")

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


		cie2 = Configuracion_Interes_Empeno()

		cie2.sucursal = sucursal2		
		cie2.almacenaje_oro = 5
		cie2.interes_oro = 6.3
		cie2.iva_oro = 16
		cie2.almacenaje_plata = 5
		cie2.interes_plata = 6.3
		cie2.iva_plata = 16
		cie2.almacenaje_prod_varios = 7.2
		cie2.interes_prod_varios = 12.63
		cie2.iva_prod_varios = 16
		cie2.usuario_modifica = usuario
		cie2.save()

		#tipo oro, mil pesos de mutuo
		resp_1 = sucursal.fn_calcula_refrendo(1000,1)
		#tipo plata, mil pesos de mutuo
		resp_2 = sucursal.fn_calcula_refrendo(1000,2)
		#articulos varios, mil pesos de mutuo
		resp_3 = sucursal.fn_calcula_refrendo(1000,3)


		#articulos varios, mil pesos de mutuo
		resp_4 = sucursal2.fn_calcula_refrendo(1633,3)

		#esta sucursal no tiene configurado el interes, deberia devolver esatus cero
		resp_5 = sucursal3.fn_calcula_refrendo(1633,3)


		self.assertEqual(resp_1[0]["estatus"],'1')
		self.assertEqual(resp_5[0]["estatus"],'0')
		self.assertEqual(resp_1[0]["refrendo"],390)
		self.assertEqual(resp_2[0]["refrendo"],540)
		self.assertEqual(round(resp_3[0]["refrendo"],2),round(decimal.Decimal(117.70),2))

		self.assertEqual(round(resp_4[0]["refrendo"],2),round(decimal.Decimal(375.64),2))



		


class Test_Boleta_Empeno(TestCase):

	@classmethod
	def setUpTestData(cls):


		cl = Cliente()
		cl.id = 1
		cl.nombre = "prueba"
		cl.apellido_p = "prueba"
		cl.estado_civil  =1
		cl.save()

		Sucursal.objects.create(sucursal = "Sucursal de prueba")
		Sucursal.objects.create(sucursal = "Sucursal de prueba 2")
		Sucursal.objects.create(sucursal = "Sucursal de prueba 3")

		sucursal = Sucursal.objects.get(sucursal = "Sucursal de prueba" )
		sucursal2 = Sucursal.objects.get(sucursal = "Sucursal de prueba 2" )
		sucursal3 = Sucursal.objects.get(sucursal = "Sucursal de prueba 3" )

		User.objects.create(username = "jasso208")
		usuario = User.objects.get(username = "jasso208")

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

		cie2 = Configuracion_Interes_Empeno()

		cie2.sucursal = sucursal2		
		cie2.almacenaje_oro = 5
		cie2.interes_oro = 6.3
		cie2.iva_oro = 16
		cie2.almacenaje_plata = 5
		cie2.interes_plata = 6.3
		cie2.iva_plata = 16
		cie2.almacenaje_prod_varios = 7.2
		cie2.interes_prod_varios = 12.63
		cie2.iva_prod_varios = 16
		cie2.usuario_modifica = usuario
		cie2.save()

		tp = Tipo_Producto()
		tp.id = 1
		tp.tipo_producto = "oro"
		tp.save()

		
		pl = Plazo()
		pl.plazo = "4 semanas"
		pl.id = 1
		pl.save()

		eb = Estatus_Boleta()
		eb.id = 1
		eb.estatus = "ABIERTA"
		eb.save()


	def test_fn_calcula_refrendo_mismo_mutuo(self):
		sucursal = Sucursal.objects.get(sucursal = "Sucursal de prueba" )
		sucursal2 = Sucursal.objects.get(sucursal = "Sucursal de prueba 2" )

		usuario = User.objects.get(username = "jasso208")

		tp = Tipo_Producto.objects.get(tipo_producto = "oro")		
		caja = None
		avaluo = 2000
		mutuo = 1000

		hoy = date.today()
		fecha_vencimiento = datetime.combine(hoy,time.min)#para la prueba  no importa la fecha de vencimiento

		cliente = Cliente.objects.get(id = 1)

		nombre_cotitular = "test_1"
		apellido_paterno = ""
		apellido_materno = ""

		plazo=Plazo.objects.get(id=1)
		
		fecha_vencimiento_real = fecha_vencimiento

		estatus_boleta = Estatus_Boleta.objects.get(id=1)#boleta abierta
		
		tm = None

		
		boleta = Boleta_Empeno.nuevo_empeno(sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus_boleta,1,tm)


		#almacenaje_oro = 10
		#interes_oro = 20
		#iva_oro = 30
		resp = boleta.fn_calcula_refrendo()
		self.assertEqual(resp[0]["estatus"],"1")
		self.assertEqual(decimal.Decimal(resp[0]["almacenaje"]),decimal.Decimal("100.00"))
		self.assertEqual(decimal.Decimal(resp[0]["interes"]),decimal.Decimal("200.00"))
		self.assertEqual(decimal.Decimal(resp[0]["iva"]),decimal.Decimal("90.00"))

		#cambiamos el porcentaje de refrendo
		r = Configuracion_Interes_Empeno.fn_set_configuracion_interes_empeno(sucursal,15,25,35,45,55,65,75,85,95,usuario)

		
		#almacenaje_oro = 15
		#interes_oro = 25
		#iva_oro = 35
		resp = boleta.fn_calcula_refrendo()
		
		#cambiamos los porcentajes de refrendo en la sucursal, pero la boleta que ya existe respeta el valor que tenia
		self.assertEqual(r,True)
		self.assertEqual(resp[0]["estatus"],"1")
		self.assertEqual(decimal.Decimal(resp[0]["almacenaje"]),decimal.Decimal("100.00"))
		self.assertEqual(decimal.Decimal(resp[0]["interes"]),decimal.Decimal("200.00"))
		self.assertEqual(decimal.Decimal(resp[0]["iva"]),decimal.Decimal("90.00"))


		#al generar una nueva boleta, se genera con los nuevos porcentajes de refrendo.				
		boleta = Boleta_Empeno.nuevo_empeno(sucursal,tp,caja,usuario,avaluo,mutuo,fecha_vencimiento,cliente,nombre_cotitular,apellido_paterno,apellido_materno,plazo,fecha_vencimiento_real,estatus_boleta,2,tm)

				#almacenaje_oro = 15
		#interes_oro = 25
		#iva_oro = 35
		resp = boleta.fn_calcula_refrendo()
		
		#cambiamos los porcentajes de refrendo en la sucursal, pero la boleta que ya existe respeta el valor que tenia
		self.assertEqual(r,True)
		self.assertEqual(resp[0]["estatus"],"1")
		self.assertEqual(decimal.Decimal(resp[0]["almacenaje"]),decimal.Decimal("150.00"))
		self.assertEqual(decimal.Decimal(resp[0]["interes"]),decimal.Decimal("250.00"))
		self.assertEqual(decimal.Decimal(resp[0]["iva"]),decimal.Decimal("140.00"))




		






		













	





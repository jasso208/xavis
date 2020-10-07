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

		

		#creamos una boleta para la prueba		
		sucursal = Sucursal.objects.get(sucursal = "prueba")
		tp = Tipo_Producto.objects.get(id = 1)
		caja = None
		usuario = User.objects.get(username="jasso208")
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










		













	





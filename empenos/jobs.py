from empenos.models import *
from empenos.funciones import *
from django.db.models import Min
import math
from datetime import date, datetime, time,timedelta
from django.db import transaction



@transaction.atomic
def fn_job_libera_apartado():
	hoy = datetime.now()
	hoy = datetime.combine(hoy,time.min)

	try:
		estatus_apartado = Estatus_Apartado.objects.get(id = 1)
		estatus_liberado = Estatus_Apartado.objects.get(id = 2)

		estatus_remate = Estatus_Boleta.objects.get(id=5)

		#obtenemos los apartados que vencen hoy
		apartados = Apartado.objects.filter(fecha_vencimiento = hoy,estatus = estatus_apartado)

		
		for a in apartados:
			
			a.estatus = estatus_liberado
			
			a.boleta.estatus = estatus_remate

			a.boleta.save()

			a.boleta = None#desvinculamos la boleta, para que pueda ser vendida o apartada nuevamente.

			a.save()
	except Exception as e:
		return false
		
		

	return True



@transaction.atomic
def fn_job_diario():

	hoy=datetime.now()#fecha actual
	hoy=datetime.combine(hoy, time.min)

	hoy=datetime(2020,11,5,0,0)	
	fecha_fin=datetime(2020,12,10,0,0)
	#cont=30

	while hoy<=fecha_fin:
		print("fecha ejecucion")
		print(hoy)
		fn_boletas_vencidas_semanal(hoy)
		fn_pagos_vencidos(hoy)
		fn_comision_pg(hoy)
		fn_boletas_10d_alomneda(hoy)
	
		dias = timedelta(days=1)	
		hoy=datetime.combine(hoy+dias, time.min)                
		

	#estas tres lineas son las que se pondran en prodcutivo
	#fn_boletas_vencidas_semanal(hoy)
	#fn_pagos_vencidos(hoy)
	#fn_comision_pg(hoy)
	#fn_boletas_10d_alomneda(hoy)

	return True

#buscamos las boletas que ya tienen 10 dias en almoneda,
#y le cambiamos el estatus a remate.
@transaction.atomic
def fn_boletas_10d_alomneda(hoy):
	estatus_remate=Estatus_Boleta.objects.get(id=5)
	estatus_almoneda=Estatus_Boleta.objects.get(id=3)

	#obtenemos todas las boletas que estan en almoneda
	boletas=Boleta_Empeno.objects.filter(estatus=estatus_almoneda)

	for b in boletas:
		dias=abs((hoy-b.fecha_vencimiento).days)	
		if int(dias)==10:
			b.estatus=estatus_remate
			b.save()
	return True



# buscamos las boletas que vencen el dia de hoy y las marcamos con estatus almoneda.
#el mismo dia que se vence, para las boletas a 4 semanas, se genera pago semanal mas con estatus vencido =N y pagado = N
#el estatus almoneda es como decir que esta vencida.
@transaction.atomic
def fn_boletas_vencidas_semanal(hoy):
	

	diario=Plazo.objects.get(id=1)
	semanal=Plazo.objects.get(id=2)
	#obtenemos el estasus almoneda
	estatus_almoneda=Estatus_Boleta.objects.get(id=3)
	estatus_remate=Estatus_Boleta.objects.get(id=5)
	estatus_desempem=Estatus_Boleta.objects.get(id=4)
	estatus_vendido=Estatus_Boleta.objects.get(id=6)
	estatus_apartado=Estatus_Boleta.objects.get(id=7)

	refrendo_pg=Tipo_Pago.objects.get(id=3)
	vendida=Estatus_Boleta.objects.get(id=6)

	#sacamos las boletas que vencen hoy  y que no han sido desempenadas ni vendidas
	#abs((hoy-boleta.fecha_vencimiento).days)

	boletas=Boleta_Empeno.objects.filter(fecha_vencimiento=hoy).exclude(estatus=estatus_desempem).exclude(estatus=estatus_vendido).exclude(estatus=estatus_apartado)

	for b in boletas:

		#cambiamos el estatus		
		if b.plazo.id==1:
			#si el plazo de la boleta es diario, se cambia el estatus a remate
			b.estatus=estatus_remate
		else:
			b.estatus=estatus_almoneda
		b.save()

		#las de plazo diario no genera pagos.
		if b.plazo!=diario:			
			refrendo=0.00
			almacenaje=0.00
			interes=0.00
			iva=0.00

			#se calcula el refrendo para que en caso de que se haya abonado a capital, se calcule el refrendo en base al nuevo mutuo
			resp=b.fn_calcula_refrendo()
			
			if b.plazo.id==2:#si es plazo 4 semanas
				#calculamos la fecha de vencimiento
				dias = timedelta(days=7)		                
				fecha_vencimiento=datetime.combine(hoy+dias, time.min)
				fecha_vencimiento_real=fecha_vencimiento
				
				fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

				almacenaje=decimal.Decimal(resp[0]["almacenaje"])/decimal.Decimal(4.00)
				interes=decimal.Decimal(resp[0]["interes"])/decimal.Decimal(4.00)
				iva=decimal.Decimal(resp[0]["iva"])/decimal.Decimal(4.00)
				refrendo=round(decimal.Decimal(resp[0]["refrendo"])/decimal.Decimal(4.00))

				#generamos el nuevo pago
				p=Pagos()
				p.tipo_pago=refrendo_pg
				p.boleta=b
				p.fecha_vencimiento=fecha_vencimiento
				p.almacenaje=almacenaje
				p.interes=interes
				p.iva=iva
				p.importe=refrendo
				p.vencido="N"
				p.pagado="N"
				p.fecha_vencimiento_real=fecha_vencimiento_real				
				p.save()

			elif b.plazo.id==3:#si es plazo de 1 mes
				print("en el caso de la boleta vencida el periodo Pg se genera al vencer el pago anterior.")

		


	return True


#se ejecuta a diario para buscar los Pagos vencidos
# y que no se han pagado.
#los marcamos como vencidos.
@transaction.atomic
def fn_pagos_vencidos(hoy):


	#obtenemos el estasus almoneda
	estatus_almoneda=Estatus_Boleta.objects.get(id=3)
	estatus_remate=Estatus_Boleta.objects.get(id=5)
	estatus_desempem=Estatus_Boleta.objects.get(id=4)
	estatus_vendido=Estatus_Boleta.objects.get(id=6)
	estatus_apartado=Estatus_Boleta.objects.get(id=7)


	


	#*******************************************************************************************
	#pagos de tipo refrendo que se venncen hoy
	refrendo=Tipo_Pago.objects.get(id=1)
	pagos=Pagos.objects.filter(fecha_vencimiento = hoy,tipo_pago = refrendo).exclude(boleta__estatus = estatus_desempem).exclude(boleta__estatus = estatus_vendido).exclude(boleta__estatus = estatus_apartado)
	estatus_almoneda=Estatus_Boleta.objects.get(id=3)
	refrendo_pg=Tipo_Pago.objects.get(id=3)

	#lo marcamos como vencidos.
	for p in pagos:
		p.vencido="S"
		p.save()


		#si el pago que esta venciendo es de periodo mensual.
		#generamos el Refrendo Pg.
		#el refrendo pg para plazo semanal se genera en la funcion de boletas vencidas.
		#Asumimos que la boleta  que es considerada aqui, esa activa de lo contrario no deberia haber llegado aqui.
		if p.boleta.plazo.id==3:
			if p.boleta.fecha_vencimiento==hoy:
				p.boleta.estatus=estatus_almoneda
			refrendo=0.00
			almacenaje=0.00
			interes=0.00
			iva=0.00

			#se calcula el refrendo para que en caso de que se haya abonado a capital, se calcule el refrendo en base al nuevo mutuo			
			resp=p.boleta.fn_calcula_refrendo()

			almacenaje=resp[0]["almacenaje"]
			interes=resp[0]["interes"]
			iva=resp[0]["iva"]
			refrendo=resp[0]["refrendo"]
			
			est_refrendo=Tipo_Pago.objects.get(id=1)
			est_comisionpg=Tipo_Pago.objects.get(id=2)
			est_refrendopg=Tipo_Pago.objects.get(id=3)

			cont_ref=Pagos.objects.filter(boleta=p.boleta,tipo_pago=est_refrendo).count()
			cont_refpg=Pagos.objects.filter(boleta=p.boleta,tipo_pago=est_refrendopg).count()

			meses=int(cont_ref)+int(cont_refpg)+1

			#como ya se pago el refrendo actual, se genera un nuevo pago tipo refrendo.
			fecha_vencimiento=datetime.combine(fn_add_months(p.boleta.fecha,meses), time.min)

			fecha_vencimiento_real=fecha_vencimiento
			
			#fecha_vencimiento=datetime.combine(fn_add_months(hoy,1), time.min)	
			#validmoas que la fecha de vencimiento no sea de azueto
			fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

			#generamos el nuevo pago
			pago=Pagos()
			pago.tipo_pago=refrendo_pg
			pago.boleta=p.boleta
			pago.fecha_vencimiento=fecha_vencimiento
			pago.almacenaje=almacenaje
			pago.interes=interes
			pago.iva=iva
			pago.importe=round(refrendo)
			pago.vencido="N"
			pago.pagado="N"
			pago.fecha_vencimiento_real=fecha_vencimiento_real
			print("entro entro 1 2")
			pago.save()	

			p.boleta.refrendo=round(refrendo)
			p.boleta.save()

			#generamos los pagos parciales.
			fn_pago_parcial(p.boleta,hoy,refrendo,pago)	

	#marcamos los periodos como vencidos,
	#aplica solo para boletas de periodo mensual.
	per=Periodo.objects.filter(pagado="N",fecha_vencimiento=hoy)
	for x in per:
		x.vencido="S"
		x.save()


	#*******************************************************************************************
	#pagos de tipo Comision PG que se venncen hoy
	comision_pg=Tipo_Pago.objects.get(id=2)
	pagos=Pagos.objects.filter(fecha_vencimiento=hoy,pagado='N',tipo_pago=comision_pg)

	#lo marcamos como vencidos.
	for p in pagos:
		p.vencido="S"
		p.save()

	#*******************************************************************************************
	#pagos de tipo refrendo PG que se vencen hoy
	refrendo_pg=Tipo_Pago.objects.get(id=3)

	pagos=Pagos.objects.filter(fecha_vencimiento=hoy,pagado='N',tipo_pago=refrendo_pg).exclude(boleta__estatus = estatus_desempem).exclude(boleta__estatus = estatus_vendido).exclude(boleta__estatus = estatus_apartado)

	for p in pagos:
		#marcamos cadapago como vencido.
		p.vencido="S"
		p.save()

		#generamos un nuevo pago de periodo de gracia.
		refrendo=0.00
		almacenaje=0.00
		interes=0.00
		iva=0.00

		#obtenemos la boleta.
		b=p.boleta

		#se calcula el refrendo para que en caso de que se haya abonado a capital, se calcule el refrendo en base al nuevo mutuo
		resp=b.fn_calcula_refrendo()

		#calculamos la fecha de vencimiento
		if b.plazo.id==2:#si es plazo 4 semanas
			dias = timedelta(days=7)		                
			fecha_vencimiento=datetime.combine(hoy+dias, time.min)
			fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)
			fecha_vencimiento_real=fecha_vencimiento

			almacenaje=decimal.Decimal(resp[0]["almacenaje"])/decimal.Decimal(4.00)
			interes=decimal.Decimal(resp[0]["interes"])/decimal.Decimal(4.00)
			iva=decimal.Decimal(resp[0]["iva"])/decimal.Decimal(4.00)
			refrendo=round(decimal.Decimal(resp[0]["refrendo"])/decimal.Decimal(4.00))

		elif b.plazo.id==3:#si es plazo de 1 mes
			#fecha_vencimiento=datetime.combine(fn_add_months(hoy,1), time.min)	
			#validmoas que la fecha de vencimiento no sea de azueto
			#fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

			est_refrendo=Tipo_Pago.objects.get(id=1)
			est_comisionpg=Tipo_Pago.objects.get(id=2)
			est_refrendopg=Tipo_Pago.objects.get(id=3)

			cont_ref=Pagos.objects.filter(boleta=p.boleta,tipo_pago=est_refrendo).count()
			cont_refpg=Pagos.objects.filter(boleta=p.boleta,tipo_pago=est_refrendopg).count()

			meses=int(cont_ref)+int(cont_refpg)+1


			#como ya se pago el refrendo actual, se genera un nuevo pago tipo refrendo.
			fecha_vencimiento=datetime.combine(fn_add_months(p.boleta.fecha,meses), time.min)

			fecha_vencimiento_real=fecha_vencimiento
			
			#fecha_vencimiento=datetime.combine(fn_add_months(hoy,1), time.min)	
			#validmoas que la fecha de vencimiento no sea de azueto
			fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

			almacenaje=resp[0]["almacenaje"]
			interes=resp[0]["interes"]
			iva=resp[0]["iva"]
			refrendo=round(resp[0]["refrendo"])		

		#elif b.plazo.id=1:
		#	print("el plazo de 1  dia no debera entrar aqui ya que no genera REEFRENDO PG")
		#generamos el nuevo pago
		pago=Pagos()
		pago.tipo_pago=refrendo_pg
		pago.boleta=b
		pago.fecha_vencimiento=fecha_vencimiento
		pago.almacenaje=almacenaje
		pago.interes=interes
		pago.iva=iva
		pago.importe=refrendo
		pago.vencido="N"
		pago.pagado="N"		
		pago.fecha_vencimiento_real=fecha_vencimiento_real
		
		pago.save()

		#si el pago que esta venciendo es de periodo mensual.
		#generamos los periodos
		#el refrendo pg para plazo semanal se genera en la funcion de boletas vencidas.
		if b.plazo.id==3:
			fn_pago_parcial(b,hoy,refrendo,pago)	


	return True

#se ejecuta a diario para generar los pagos diario de tipo Comision Pg
@transaction.atomic
def fn_comision_pg(hoy):
	#el estatus almoneda (boleta vencida)
	estatus_almoneda=Estatus_Boleta.objects.get(id=3)
	estatus_remate=Estatus_Boleta.objects.get(id=5)

	plazo_1_dia=Plazo.objects.get(id=1)

	#buscamos todas las boletas en almoneda y remate,# las boletas con plazo de 1 dia no generan pagos.
	boletas=Boleta_Empeno.objects.filter(estatus=estatus_almoneda).exclude(plazo=plazo_1_dia) | Boleta_Empeno.objects.filter(estatus=estatus_remate).exclude(plazo=plazo_1_dia)

	for b in boletas:

		#esta condicion es necesaria por si se requiere ejecutar un dia manualmente.
		if hoy>=b.fecha_vencimiento:
			#obtenmos los dias que lleva la boleta vencida.
			dias_vencido=abs((hoy-b.fecha_vencimiento).days)
		else:
			dias_vencido=-1

		comision_pg=Tipo_Pago.objects.get(id=2)

		dias = timedelta(days=1)	
		fecha_vencimiento=datetime.combine(hoy+dias, time.min)


		if dias_vencido>=0:
			compg=b.mutuo*0.0073
			p=Pagos()
			p.tipo_pago=comision_pg
			p.boleta=b
			p.fecha_vencimiento=fecha_vencimiento
			p.almacenaje=0
			p.interes=0
			p.iva=compg/1.16
			p.importe=math.ceil(compg)
			p.vencido="N"
			p.pagado="N"
			p.fecha_vencimiento_real=fecha_vencimiento
			p.save()



		#si lleva tres dias la boleta venida, generamos 3 pagos de tipo Comision PG con estatus vencida
		# y un pago de tipo Cmosion PG con estatus vigente que vence manana.		
		#if dias_vencido==3:
		#	#*****************************************************************************************
		#	dias = timedelta(days=1)	
		#	fecha_vencimiento=datetime.combine(b.fecha_vencimiento+dias, time.min)

		#	compg=b.mutuo*0.0073
		#	p=Pagos()
		#	p.tipo_pago=comision_pg
		#	p.boleta=b
		#	p.fecha_vencimiento=fecha_vencimiento
		#	p.almacenaje=0
		#	p.interes=0
		#	p.iva=compg/1.16
		#	p.importe=math.ceil(compg)
		#	p.vencido="S"
		#	p.pagado="N"
		#	p.save()
		#	#*****************************************************************************************
		#	dias = timedelta(days=2)	
		#	fecha_vencimiento=datetime.combine(b.fecha_vencimiento+dias, time.min)

		#	compg=b.mutuo*0.0073
		#	p=Pagos()
		#	p.tipo_pago=comision_pg
		#	p.boleta=b
		#	p.fecha_vencimiento=fecha_vencimiento
		#	p.almacenaje=0
		#	p.interes=0
		#	p.iva=compg/1.16
		#	p.importe=math.ceil(compg)
		#	p.vencido="S"
		#	p.pagado="N"
		#	p.save()
		#	#*****************************************************************************************
		#	dias = timedelta(days=3)	
		#	fecha_vencimiento=datetime.combine(b.fecha_vencimiento+dias, time.min)

		#	compg=b.mutuo*0.0073
		#	p=Pagos()
		#	p.tipo_pago=comision_pg
		#	p.boleta=b
		#	p.fecha_vencimiento=fecha_vencimiento
		#	p.almacenaje=0
		#	p.interes=0
		#	p.iva=compg/1.16
		#	p.importe=math.ceil(compg)
		#	p.vencido="S"
		#	p.pagado="N"
		#	p.save()
		#	#*****************************************************************************************
		#	dias = timedelta(days=4)	
		#	fecha_vencimiento=datetime.combine(b.fecha_vencimiento+dias, time.min)

		#	compg=b.mutuo*0.0073
		#	p=Pagos()
		#	p.tipo_pago=comision_pg
		#	p.boleta=b
		#	p.fecha_vencimiento=fecha_vencimiento
		#	p.almacenaje=0
		#	p.interes=0
		#	p.iva=compg/1.16
		#	p.importe=math.ceil(compg)
		#	p.vencido="N"
		#	p.pagado="N"
		#	p.save()
		#	#*****************************************************************************************
		#elif dias_vencido>3:

		#	dias = timedelta(days=1)	
		#	fecha_vencimiento=datetime.combine(hoy+dias, time.min)

		#	compg=b.mutuo*0.0073
		#	p=Pagos()
		#	p.tipo_pago=comision_pg
		#	p.boleta=b
		#	p.fecha_vencimiento=fecha_vencimiento
		#	p.almacenaje=0
		#	p.interes=0
		#	p.iva=compg/1.16
		#	p.importe=math.ceil(compg)
		#	p.vencido="N"
		#	p.pagado="N"
		#	p.save()


from empenos.models import Boleta_Empeno,Pagos,Estatus_Boleta,Plazo,Tipo_Pago
from empenos.funciones import fn_fecha_vencimiento_valida,fn_add_months,fn_calcula_refrendo
from django.db.models import Min
import math
from datetime import date, datetime, time,timedelta
from django.db import transaction
@transaction.atomic
def fn_job_diario():

	hoy=datetime.now()#fecha actual
	hoy=datetime.combine(hoy, time.min)

	hoy=datetime(2020,8,14,0,0)	
	fecha_fin=datetime(2020,9,16,0,0)

	cont=30

	while hoy<=fecha_fin:
		print("fecha ejecucion")
		print(hoy)
		fn_boletas_vencidas(hoy)
		fn_pagos_vencidos(hoy)
		fn_comision_pg(hoy)

		dias = timedelta(days=1)	
		hoy=datetime.combine(hoy+dias, time.min)                
		

	#estas tres lineas son las que se pondran en prodcutivo
	#fn_boletas_vencidas(hoy)
	#fn_pagos_vencidos(hoy)
	#fn_comision_pg(hoy)

	return True


# buscamos las boletas que vencen el dia de hoy y las marcamos con estatus almoneda.
#el mismo dia que se vence, para las boletas a 4 semanas, se genera pago semanal mas con estatus vencido =N y pagado = N
#el mismo dia que se vence, para las boletas a 1 mes, se genera 1 pago mesal mas con estatusvencido =N y pagado =N
#el estatus almoneda es como decir que esta cancelada.
@transaction.atomic
def fn_boletas_vencidas(hoy):


	diario=Plazo.objects.get(id=1)
	#obtenemos el estasus almoneda
	estatus_almoneda=Estatus_Boleta.objects.get(id=3)
	estatus_remate=Estatus_Boleta.objects.get(id=5)
	estatus_desempem=Estatus_Boleta.objects.get(id=4)


	refrendo_pg=Tipo_Pago.objects.get(id=3)

	#sacamos las boletas que vencen hoy  y que no han sido desempeñadas
	boletas=Boleta_Empeno.objects.filter(fecha_vencimiento=hoy).exclude(estatus=estatus_desempem)

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
			resp=fn_calcula_refrendo(b.mutuo,b.tipo_producto.id)

			#calculamos la fecha de vencimiento
			if b.plazo.id==2:#si es plazo 4 semanas
				dias = timedelta(days=7)		                
				fecha_vencimiento=datetime.combine(hoy+dias, time.min)
				fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

				almacenaje=resp[0]["almacenaje"]/4.00
				interes=resp[0]["interes"]/4.00
				iva=resp[0]["iva"]/4.00
				refrendo=math.ceil(resp[0]["refrendo"]/4.00)

			elif b.plazo.id==3:#si es plazo de 1 mes


				
				est_refrendo=Tipo_Pago.objects.get(id=1)
				est_comisionpg=Tipo_Pago.objects.get(id=2)
				est_refrendopg=Tipo_Pago.objects.get(id=3)

				cont_ref=Pagos.objects.filter(boleta=b,tipo_pago=est_refrendo).count()
				cont_refpg=Pagos.objects.filter(boleta=b,tipo_pago=est_refrendopg).count()

				meses=int(cont_ref)+int(cont_refpg)+1


				#como ya se pago el refrendo actual, se genera un nuevo pago tipo refrendo.
				fecha_vencimiento=datetime.combine(fn_add_months(b.fecha,meses), time.min)

				#fecha_vencimiento=datetime.combine(fn_add_months(hoy,1), time.min)	
				#validmoas que la fecha de vencimiento no sea de azueto
				fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

		

				almacenaje=resp[0]["almacenaje"]
				interes=resp[0]["interes"]
				iva=resp[0]["iva"]
				refrendo=math.ceil(resp[0]["refrendo"])				

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
			p.save()
	return True


#se ejecuta a diario para buscar los Pagos vencidos
# y que no se han pagado.
#los marcamos como vencidos.
@transaction.atomic
def fn_pagos_vencidos(hoy):

	#*******************************************************************************************
	#pagos de tipo refrendo que se venncen hoy
	refrendo=Tipo_Pago.objects.get(id=1)
	pagos=Pagos.objects.filter(fecha_vencimiento=hoy,tipo_pago=refrendo)

	#lo marcamos como vencidos.
	for p in pagos:
		p.vencido="S"
		p.save()

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
	pagos=Pagos.objects.filter(fecha_vencimiento=hoy,pagado='N',tipo_pago=refrendo_pg)

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
		resp=fn_calcula_refrendo(b.mutuo,b.tipo_producto.id)

		#calculamos la fecha de vencimiento
		if b.plazo.id==2:#si es plazo 4 semanas
			dias = timedelta(days=7)		                
			fecha_vencimiento=datetime.combine(hoy+dias, time.min)
			fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

			almacenaje=resp[0]["almacenaje"]/4.00
			interes=resp[0]["interes"]/4.00
			iva=resp[0]["iva"]/4.00
			refrendo=math.ceil(resp[0]["refrendo"]/4.00)

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

			#fecha_vencimiento=datetime.combine(fn_add_months(hoy,1), time.min)	
			#validmoas que la fecha de vencimiento no sea de azueto
			fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)





			almacenaje=resp[0]["almacenaje"]
			interes=resp[0]["interes"]
			iva=resp[0]["iva"]
			refrendo=math.ceil(resp[0]["refrendo"])		

		#elif b.plazo.id=1:
		#	print("el plazo de 1  dia no debera entrar aqui ya que no genera REEFRENDO PG")
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
		p.save()
	return True

#se ejecuta a diario para generar los pagos diario de tipo Comision Pg
@transaction.atomic
def fn_comision_pg(hoy):
	#el estatus almoneda (boleta vencida)
	estatus_almoneda=Estatus_Boleta.objects.get(id=3)

	plazo_1_dia=Plazo.objects.get(id=1)

	#buscamos todas las boletas en almoneda,# las boletas con plazo de 1 dia no generan pagos.
	boletas=Boleta_Empeno.objects.filter(estatus=estatus_almoneda).exclude(plazo=plazo_1_dia)

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


		print("dias_vencidos")
		print(dias_vencido)
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
			p.save()



		#si lleva tres dias la boleta venida, generamos 3 pagos de tipo Comision PG con estatus vencida
		# y un pago de tipo Cmosion PG con estatus vigente que vence mañana.		
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


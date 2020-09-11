
import datetime
import calendar
from empenos.models import *
from datetime import date, datetime, time,timedelta
import math
from django.db import transaction
from django.db.models import Max
import decimal
import smtplib
import email.message
from django.conf import settings
from django.db.models import Sum

def fn_calcula_precio_venta_producto(boleta):
	importe_venta=0.00

	porcentaje=Porcentaje_Sobre_Avaluo.objects.all().aggregate(Sum("porcentaje"))

	porce=0;
	if porcentaje["porcentaje__sum"]!=None:
		porce=int(porcentaje["porcentaje__sum"])

	importe_venta=decimal.Decimal(boleta.avaluo)+(decimal.Decimal(boleta.avaluo)*(decimal.Decimal(porce)/decimal.Decimal(100.00)))
	print(boleta.avaluo)
	print(boleta.avaluo)
	print(importe_venta)
	return importe_venta


def fn_calcula_refrendo(mutuo,tipo_producto):
	almacenaje=0.00
	interes=0.00
	iva=0.00
	refrendo=0.00
	respuesta=[]
	if tipo_producto==1 or tipo_producto==2:#oro o plata
		almacenaje=(mutuo*0.05)
		interes=(mutuo*0.063)
		iva=((almacenaje+interes)*0.16)
		refrendo=(almacenaje+interes+iva)
	else:
		almacenaje=(mutuo*0.072)
		interes=(mutuo*0.1263)
		iva=((almacenaje+interes)*0.16)
		refrendo=(almacenaje+interes+iva)
	respuesta.append({"almacenaje":almacenaje,"interes":interes,"iva":iva,"refrendo":refrendo})
	return respuesta

#funcion para determinar el modulo
def fn_modulo(a, b):
  '''Funcion que calcula el
  residuo (modulo) de una division'''
  residuo = 0
  x = a // b
  residuo = a - (x * b)
  return residuo
  
#solo para periodos mensuales
def fn_pago_parcial(boleta,hoy,refrendo,pago):

	#primer periodo
	print("periodo 1")
	#dias fijos
	periodo_7=Tipo_Periodo.objects.get(id=1)
	days = timedelta(days=7)
	
	fecha_vencimiento = datetime.combine(hoy+days, time.min) 
	print("fecha_vencimiento")
	print(fecha_vencimiento)
	fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)
	print("fecha_vencimiento")
	print(fecha_vencimiento)

	consecutivo=Periodo.objects.filter(boleta=boleta).aggregate(Max("consecutivo"))

	if consecutivo["consecutivo__max"]==None:
		contador=1
	else:
		contador=int(consecutivo["consecutivo__max"])+1

	per=Periodo()
	per.boleta=boleta
	per.fecha_vencimiento=fecha_vencimiento
	per.importe=decimal.Decimal(refrendo)/decimal.Decimal(4.00)
	per.tipo_periodo=periodo_7
	per.pago=pago
	per.consecutivo=contador
	per.save()

	contador=contador+1

	print("periodo 2")
	#segundo periodo
	#dias fijos
	periodo_7=Tipo_Periodo.objects.get(id=1)
	days = timedelta(days=14)
	
	fecha_vencimiento = datetime.combine(hoy+days, time.min) 
	fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

	per=Periodo()
	per.boleta=boleta
	per.fecha_vencimiento=fecha_vencimiento
	per.importe=decimal.Decimal(refrendo)/decimal.Decimal(4.0)					
	per.tipo_periodo=periodo_7
	per.pago=pago
	per.consecutivo=contador
	per.save()

	contador=contador+1
	print("periodo 3")
	#tercer periodo
	#dias fijos
	periodo_7=Tipo_Periodo.objects.get(id=1)
	days = timedelta(days=21)
	
	fecha_vencimiento = datetime.combine(hoy+days, time.min) 
	fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

	per=Periodo()
	per.boleta=boleta
	per.fecha_vencimiento=fecha_vencimiento
	per.importe=decimal.Decimal(refrendo)/decimal.Decimal(4.0)					
	per.tipo_periodo=periodo_7
	per.pago=pago
	per.consecutivo=contador
	per.save()

	contador=contador+1

	print("periodo 4")
	#cuarto periodo
	#dias variable
	periodo_variable=Tipo_Periodo.objects.get(id=2)

	per=Periodo()
	per.boleta=boleta
	per.fecha_vencimiento=pago.fecha_vencimiento
	per.importe=decimal.Decimal(refrendo)/decimal.Decimal(4.0)					
	per.tipo_periodo=periodo_variable
	per.pago=pago
	per.consecutivo=contador
	per.save()


def fn_add_months(sourcedate, months):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month // 12
	month = month % 12 + 1
	day = min(sourcedate.day, calendar.monthrange(year,month)[1])
	return date(year, month, day)

#valida que la fecha de vencimiento no caiga en algun dia de azueto, 
#en caso de caer en dia de azueto, le asigna el siguiente dia habil.
def fn_fecha_vencimiento_valida(fecha_vencimiento):
	try:
		#si el dia es de azueto, buscamos el siguiente hata encontrar un dia que no sea de azueto.
		dv=Dia_No_Laboral.objects.get(fecha=fecha_vencimiento)

		dia_mas = timedelta(days=1)
		#si la fecha de vencimiento existe en los dias inhabiles, buscamos el siguiente dia para que sea el de vencimiento.
		fecha_vencimiento=datetime.combine(fecha_vencimiento+dia_mas, time.min)

		dv=Dia_No_Laboral.objects.get(fecha=fecha_vencimiento)
		dia_mas = timedelta(days=1)

		#si la fecha de vencimiento existe en los dias inhabiles, buscamos el siguiente dia para que sea el de vencimiento.
		fecha_vencimiento=datetime.combine(fecha_vencimiento+dia_mas, time.min)

		dv=Dia_No_Laboral.objects.get(fecha=fecha_vencimiento)
		dia_mas = timedelta(days=1)

		#si la fecha de vencimiento existe en los dias inhabiles, buscamos el siguiente dia para que sea el de vencimiento.
		fecha_vencimiento=datetime.combine(fecha_vencimiento+dia_mas, time.min)

		dv=Dia_No_Laboral.objects.get(fecha=fecha_vencimiento)
		dia_mas = timedelta(days=1)

		#si la fecha de vencimiento existe en los dias inhabiles, buscamos el siguiente dia para que sea el de vencimiento.
		fecha_vencimiento=datetime.combine(fecha_vencimiento+dia_mas, time.min)

	except Exception as e:
		print(e)
		print("la fecha de vencimiento es valida")
	return  fecha_vencimiento


def fn_calcula_saldo_refrendo(boleta,hoy):

	est_refrendo=Tipo_Pago.objects.get(id=1)	
	estatus_activo=Estatus_Boleta.objects.get(id=1)
	importe_refrendo=0.00

	if boleta.estatus==estatus_activo:#cuando la boleta este activa		
		if boleta.plazo.id==2:#4 semanas
			#obtanemos los abonos que no estan vencidos y no han sido pagados.
			pagos=Pagos.objects.filter(vencido="N",pagado="N",boleta=boleta).order_by("fecha_vencimiento")

			dias = timedelta(days=6)				

			fecha_emision=datetime.combine(boleta.fecha, time.min)

			d = timedelta(days=7)

			#ok
			if fecha_emision==hoy:#si se esta consultando el dia que se emitio la boleta
				cont=0
				for p in pagos:

					if cont==0 :
						fecha_abono=datetime.combine(p.fecha_vencimiento-d,time.min)
						
						if fecha_abono==hoy:#validamos que el primer abono a liqudar sea el primer abono generado
							importe_refrendo=decimal.Decimal(importe_refrendo)+decimal.Decimal(p.importe)
					cont=1
			else:				
				for p in pagos:
					fecha_i=datetime.combine(p.fecha_vencimiento-dias, time.min)                
					if p.fecha_vencimiento>=hoy and fecha_i<= hoy:
						#este es el pago que esta corriendo actualmente.
						pago_actual=p
						importe_refrendo=decimal.Decimal(importe_refrendo)+decimal.Decimal(p.importe)

			#obtenemos los pagos que ya vencieron
			pagos_2=Pagos.objects.filter(vencido="S",pagado="N",boleta=boleta)			

			for p in pagos_2:
				importe_refrendo=importe_refrendo+p.importe

		elif boleta.plazo.id==3:#1 mes			
			pago_actual=Pagos.objects.get(vencido="N",pagado="N",boleta=boleta)
			cont_boleta_no_vencida=Pagos.objects.filter(vencido="N",boleta=boleta).count()


			#si tiene mas de una boleta no vencida, quiere decir que ya se pago el mes actual.
			#
			if int(cont_boleta_no_vencida)>1:
				importe_refrendo=0
			else:				
				importe_refrendo=pago_actual.importe

	else:#cuando la boleta esta e almoneda o remate
		#cuando la boleta esta vencida todos los pagos tipo refrendo estan vencidos.
		pagos=Pagos.objects.filter(tipo_pago=est_refrendo,vencido="S",pagado="N",boleta=boleta)
		for x in pagos:
			type(importe_refrendo)
			type(x.importe)
			importe_refrendo=decimal.Decimal(importe_refrendo)+decimal.Decimal(x.importe)

	return importe_refrendo


#calcula el saldo de los pagos de tipo RefrendoPG que no han sido pagados.
def fn_saldo_refrendopg(boleta):	
	est_refrendopg=Tipo_Pago.objects.get(id=3)

	#buscamos todos los pagos de tipo Refrendo PG que no han sido pagados.
	pago=Pagos.objects.filter(tipo_pago=est_refrendopg,boleta=boleta,pagado="N")
	importe_refrendopg=0.00

	for x in pago:
		importe_refrendopg=decimal.Decimal(importe_refrendopg)+decimal.Decimal(x.importe)
	return importe_refrendopg


def fn_saldo_comisionpg(boleta):
	est_comisionpg=Tipo_Pago.objects.get(id=2)	

	#buscamos todos los pagos de tipo Refrendo PG que no han sido pagados.
	pago=Pagos.objects.filter(tipo_pago=est_comisionpg,boleta=boleta,pagado="N")
	importe_comisionpg=0.00

	for x in pago:
		importe_comisionpg=decimal.Decimal(importe_comisionpg)+decimal.Decimal(x.importe)
		
	return importe_comisionpg	


#recivimos el abono y determinamos el importe que afecto a refrendos.
def fn_importe_a_refrendo(abono):
	importe=0.00

	#plazo semanal
	if abono.boleta.plazo.id==2:
		importe_r=Rel_Abono_Pago.objects.filter(abono=abono)

		ir=0.00
		for x in importe_r:
			if x.pago.tipo_pago.id!=2:#validamos quel pago no sea comsiion pg
				ir=decimal.Decimal(ir)+decimal.Decimal(x.pago.importe)

	#plazo mensual
	if abono.boleta.plazo.id==3:
		importe_p=Rel_Abono_Periodo.objects.filter(abono=abono)
		ir=decimal.Decimal(0.00)
		for x in importe_p:
			ir=ir+decimal.Decimal(x.periodo.importe)


	return math.ceil(ir)


#recivimos el abono y determinamos el importe que afecto a comision pg.
def fn_importe_a_pg(abono):	

	importe_r=Rel_Abono_Pago.objects.filter(abono=abono)

	ir=0.00
	for x in importe_r:
		if x.pago.tipo_pago.id==2:#validamos quel pago no sea comsiion pg
			ir=decimal.Decimal(ir)+decimal.Decimal(x.pago.importe)

	return ir

def fn_importe_a_cap(abono):
	importe=0.00
	try:
		ra=Rel_Abono_Capital.objects.get(abono=abono)
		
		if decimal.Decimal(ra.capital_restante)!=decimal.Decimal(0):#si es cero, es que fue desempeño, por lo tanto no es abono a capital
			importe=decimal.Decimal(importe)+decimal.Decimal(ra.importe)
	except Exception as e:
		print(e)
		print("no abono a capital")

	return importe


def fn_importe_desemp(abono):
	importe=0.00
	try:
		ra=Rel_Abono_Capital.objects.get(abono=abono)
		
		if decimal.Decimal(ra.capital_restante)==decimal.Decimal(0):#si el capital restanto no es cero, es que es abono a capital, y no se considera aqui
			importe=decimal.Decimal(importe)+decimal.Decimal(ra.importe)
	except Exception as e:
		print(e)
		print("no abono a capital")

	return importe




#antes de aceptar un refrendo, en la pantalla existe un boton que simula como quedaria la boeleta del cliente.
# es este boton el que ejecuta esta funcion.
#en pagos temp ya tenemos cargados todos los pagos de la boleta.
@transaction.atomic
def fn_simula_refrendo(importe_abono,usuario,boleta,recursivo):	

	hoy=datetime.now()#fecha actual
	hoy=datetime.combine(hoy, time.min)



	est_refrendo=Tipo_Pago.objects.get(id=1)
	est_comisionpg=Tipo_Pago.objects.get(id=2)
	est_refrendopg=Tipo_Pago.objects.get(id=3)


	

	#si recursivo es 0 es que es un abono de boleta activa
	if int(recursivo)==0:
		fecha_vencimiento=boleta.fecha_vencimiento_real
	else:# si recursivo es 1, es que viene de una boleta vencida.
		#Cambiamos temporalemente el estatus de la boleta a activa para acceder al algoritmo de boletas activas.
		estatus_activo=Estatus_Boleta.objects.get(id=1)
		

		estatus_respaldo=boleta.estatus#guardamos el estatus en que se encuentra la boleta para poder regresarla a su estatus.

		boleta.estatus=estatus_activo
		boleta.save()

		try:
			refrendopg=Pagos_Temp.objects.filter(tipo_pago=est_refrendopg,usuario=usuario)

			if refrendopg.exists():
				fe_ve=Pagos_Temp.objects.filter(tipo_pago=est_refrendopg,usuario=usuario).aggregate(Max("fecha_vencimiento_real"))

				fecha_vencimiento=fe_ve["fecha_vencimiento_real__max"]
			else:
				fecha_vencimiento=boleta.fecha_vencimiento_real	
		except:
			fecha_vencimiento=boleta.fecha_vencimiento_real

	mutuo=boleta.mutuo

	#boleta Activa / Abierta
	if boleta.estatus.id==1:

		if int(recursivo)!=0:
			#regresamos el estatus de la boleta.
			boleta.estatus=estatus_respaldo
			boleta.save()

		if boleta.plazo.id==2:#semanal			
			#obtenemos todos los pagos tipo refrendo que no ha sido pagados.
			pagos_t=Pagos_Temp.objects.filter(usuario=usuario,tipo_pago=est_refrendo,pagado="N").order_by("fecha_vencimiento_real")



			fec_boleta=datetime.combine(boleta.fecha,time.min)

			if fec_boleta==hoy:
				dias = timedelta(days=7)	
			else:
				dias = timedelta(days=6)	
			
			pag=Pagos_Temp.objects.filter(usuario=usuario,tipo_pago=est_refrendo,pagado="N")
			



			#obtenemos el pago que esta corriendo actualmente
			pag_actual=None
			for p in pag:
				
				fecha_i=datetime.combine(p.fecha_vencimiento-dias, time.min)                
				if p.fecha_vencimiento>=hoy and fecha_i<= hoy:
					#este es el pago que esta corriendo actualmente.
					pag_actual=p

			print("fecha_vencimiento")
			print(fecha_vencimiento)
			
			fecha_vencimiento_real=fecha_vencimiento
			refrendo_pendiente=fn_calcula_saldo_refrendo(boleta,hoy)

			pag_ac=0#cuando es cero es que no se a cubierto el pago actual, cuando cambia a 1 esque ya se cubrio el pago actual.
			#marcamos los pagos afectados como pagados.
			for pt in pagos_t:

				

				if int(importe_abono)>=pt.importe and int(pag_ac)==0 and refrendo_pendiente>0:	
					

					#print("id: "+str(pt.id)+";fecha_vencimiento: "+str(pt.fecha_vencimiento)+"; importe: "+str(pt.importe)+"; importe_abono"+str(importe_abono))
					
					pt.pagado="S"
					pt.save()
					
					#por cada pago tipo refrendo pagado, generamos uno nuevo.
					dias = timedelta(days=7)
					print("entro aqui antes de pagos_temp")		                
					print(fecha_vencimiento_real)
					fecha_vencimiento=datetime.combine(fecha_vencimiento_real+dias, time.min)
					
					fecha_vencimiento_real=fecha_vencimiento

					fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)
					

					npt=Pagos_Temp()
					npt.usuario=pt.usuario
					npt.tipo_pago=pt.tipo_pago
					npt.boleta=pt.boleta
					npt.fecha_vencimiento=fecha_vencimiento
					npt.almacenaje=pt.almacenaje
					npt.interes=pt.interes
					npt.iva=pt.iva
					npt.importe=pt.importe
					npt.vencido="N"
					npt.pagado="N"
					ntp.fecha_vencimiento_real=fecha_vencimiento_real
					npt.save()
					importe_abono=int(importe_abono)-int(pt.importe)#disminuimos el saldo del importe abonado
					if pag_actual==pt:
						pag_ac=1
						print("encontro el apgo actual")

			num_pagos_no_vencidos=int(Pagos_Temp.objects.filter(usuario=usuario,vencido="N",pagado='N',tipo_pago=est_refrendo).count())


			#si el importe del abono es mayor a cero
			#y el numero de abonos no vencidos es 4
			# y no estamos en el periodo de algun refrendo no vencido.
			if int(importe_abono)>0 and (int(num_pagos_no_vencidos))==4:
		
				mutuo=boleta.mutuo

				mutuo=int(mutuo)-int(importe_abono)

				#actualizamos el refrendo en base al nuevo mutuo
				ref=fn_calcula_refrendo(mutuo,boleta.tipo_producto.id)

				refrendo=math.ceil((ref[0]["refrendo"])/4)
				almacenaje=ref[0]["almacenaje"]/4
				interes=ref[0]["interes"]/4
				iva=ref[0]["iva"]/4

				pagos_t=Pagos_Temp.objects.filter(pagado="N",tipo_pago=est_refrendo,usuario=usuario).order_by("fecha_vencimiento")

				#actualizamos el importe de los refrendos en base al nuevo mutuo
				for pt in pagos_t:
					if mutuo!=0:
						pt.importe=refrendo
						pt.almacenaje=almacenaje
						pt.interes=interes
						pt.iva=iva
						pt.save()
					else:
						pt.delete()

			return mutuo#retornamos el nuevo mutuo

		elif boleta.plazo.id==3:#mensual		
			#la boleta esta activa y es plazo mensual.			
			

			
			hoy=datetime.now()#fecha actual
			hoy=datetime.combine(hoy, time.min)

			if int(recursivo)==1:
				#cuando es recursiva es que se trata de una boleta vencida, por lo tanto sus pagos tiporefrendo estan vencidos pero debe haber uno sin pagar
				pagos_t=Pagos_Temp.objects.get(usuario=usuario,tipo_pago=est_refrendo,pagado="N")
				fec_aux=hoy
			else:
				#como la boleta esta activa y es plazo mensual, solo debe tener un pago mensual vigente y sin pagar
				pagos_t=Pagos_Temp.objects.get(usuario=usuario,tipo_pago=est_refrendo,vencido="N",pagado="N")

				fec_aux=datetime.combine(fn_add_months(pagos_t.fecha_vencimiento,-1), time.min)	


			#si tiene mas de 1 pago no vencido, es que se pago el mes aque esta corriendo actualmetne y se genero uno nuevo
			# por lo tanto, ya no afecta a pagos, afecta a capital.
			cont_pagos_vencidos=Pagos_Temp.objects.filter(usuario=usuario,tipo_pago=est_refrendo,vencido="N").count()









			if (int(cont_pagos_vencidos)==1 or int(recursivo)==1) and (fec_aux<=hoy):
				
				#marcamos el pago como pagado.
				pagos_t.pagado="S"
				pagos_t.save()


				cont_ref=Pagos_Temp.objects.filter(usuario=usuario,tipo_pago=est_refrendo).count()
				cont_refpg=Pagos_Temp.objects.filter(usuario=usuario,tipo_pago=est_refrendopg).count()

				meses=int(cont_ref)+int(cont_refpg)+1

				#como ya se ppago el refrendo actual, se genera un nuevo pago tipo refrendo.
				fecha_vencimiento=datetime.combine(fn_add_months(boleta.fecha,meses), time.min)

				#validmoas que la fecha de vencimiento no sea de azueto
				fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)


				npt=Pagos_Temp()
				npt.usuario=pagos_t.usuario
				npt.tipo_pago=pagos_t.tipo_pago
				npt.boleta=pagos_t.boleta
				npt.fecha_vencimiento=fecha_vencimiento
				npt.almacenaje=pagos_t.almacenaje
				npt.interes=pagos_t.interes
				npt.iva=pagos_t.iva
				npt.importe=pagos_t.importe
				npt.vencido="N"
				npt.pagado="N"
				npt.save()

				importe_abono=int(importe_abono)-int(pagos_t.importe)#disminuimos el saldo del importe abonado

			num_pagos_no_pagados=int(Pagos_Temp.objects.filter(usuario=usuario,pagado="N",tipo_pago=est_refrendo).count())

			#si entramos ene sesta condicion es porque estamos en el periodo de un refrendo PG
			if fec_aux>=hoy:
				num_pagos_no_pagados=num_pagos_no_pagados+1

			#si es mayor a cero
			#y el num de pagos no pagados es 2 , abonamos a capital.
			if (int(importe_abono)>0 and (int(num_pagos_no_pagados)==2) or (int(num_pagos_no_pagados)==1 and int(recursivo)!=0)):

				mutuo=boleta.mutuo
				mutuo=int(mutuo)-int(importe_abono)

				#actualizamos el refrendo en base al nuevo mutuo
				ref=fn_calcula_refrendo(mutuo,boleta.tipo_producto.id)

				refrendo=math.ceil((ref[0]["refrendo"]))
				almacenaje=ref[0]["almacenaje"]
				interes=ref[0]["interes"]
				iva=ref[0]["iva"]

				npt=Pagos_Temp.objects.get(usuario=usuario,vencido="N",pagado="N",tipo_pago=est_refrendo)

				#si el mutuo es mayor a cero, actualizamos el importe de los pagos tipo refrendo
				if mutuo!=0:

					npt.importe=refrendo
					npt.almacenaje=almacenaje
					npt.interes=interes
					npt.iva=iva
					npt.save()
					
				else:# si el mutuo es cero, borramos el pago recien generado.
					npt.delete()
					#pagos_t.delete()
			return mutuo#retornamos el nuevo mutuo

	else:


		est_comisionpg=Tipo_Pago.objects.get(id=2)
		est_refrendopg=Tipo_Pago.objects.get(id=3)

		#todos los pagos comision Pg deben ser cubiertos 
		pagos_comisionpg=Pagos_Temp.objects.filter(usuario=usuario,tipo_pago=est_comisionpg,pagado="N")
		for pcg in pagos_comisionpg:
			pcg.pagado="S"
			pcg.save()

			importe_abono=int(importe_abono)-int(pcg.importe)#disminuimos el saldo del importe abonado




		#todos los pagos comision Pg deben ser cubiertos 
		pagos_refrendopg=Pagos_Temp.objects.filter(usuario=usuario,tipo_pago=est_refrendopg,pagado="N")

		#pf_temporal=None
		#fv_final=boleta.fecha_vencimiento

		#para contar a cuantos refrendos pg afecto		
		for prg in pagos_refrendopg:			
			prg.pagado="S"
			prg.save()
			
			importe_abono=int(importe_abono)-int(prg.importe)#disminuimos el saldo del importe abonado

			#calculamos la nueva fecha de vencimiento
			#se toma la mas alta fecha devencimiento de Refrendo Pg
			#if prg.fecha_vencimiento>fv_final:
			#	fv_final=prg.fecha_vencimiento

		#boleta.fecha_vencimiento=fv_final
		#boleta.save()


		

		if importe_abono>0:
			#recursividad para acceder al algoritmo de una boleta activa.
			return fn_simula_refrendo(importe_abono,usuario,boleta,1)
		else:
			return boleta.mutuo




#falta replicar el cambio de la simulacion pero en el real.
@transaction.atomic
def fn_aplica_refrendo(usuario,importe_abono,caja,boleta,recursivo,abono=None):
	hoy=datetime.now()#fecha actual
	hoy=datetime.combine(hoy, time.min)

	if abono==None:

		try:
			Imprime_Abono.objects.get(usuario=usuario,abono=abono).delete()
		except:
			print("")
		tm=Tipo_Movimiento.objects.get(id=5)
		
		folio=fn_folios(tm,boleta.sucursal)

		abono=Abono()
		abono.usuario=usuario
		abono.importe=importe_abono
		abono.caja=caja
		abono.boleta=boleta
		abono.folio=folio
		abono.tipo_movimiento=tm
		abono.sucursal=boleta.sucursal

		abono.save()

		ia=Imprime_Abono()
		ia.usuario=usuario
		ia.abono=abono
		ia.save()


	est_refrendo=Tipo_Pago.objects.get(id=1)
	est_comisionpg=Tipo_Pago.objects.get(id=2)
	est_refrendopg=Tipo_Pago.objects.get(id=3)

	#tipo de pago refrendo
	est_refrendo=Tipo_Pago.objects.get(id=1)

		#si recursivo es 0 es que es un abono de boleta activa
	if int(recursivo)==0:
		fecha_vencimiento=boleta.fecha_vencimiento_real
	else:# si recursivo es 1, es que viene de una boleta vencida.
		#Cambiamos temporalemente el estatus de la boleta a activa para acceder al algoritmo de boletas activas.
		estatus_activo=Estatus_Boleta.objects.get(id=1)
		

		estatus_respaldo=boleta.estatus#guardamos el estatus en que se encuentra la boleta para poder regresarla a su estatus.

		boleta.estatus=estatus_activo
		boleta.save()

		try:
			refrendopg=Pagos.objects.filter(tipo_pago=est_refrendopg,boleta=boleta)

			if refrendopg.exists():
				fe_ve=Pagos.objects.filter(tipo_pago=est_refrendopg,boleta=boleta).aggregate(Max("fecha_vencimiento_real"))
				p=Pagos.objects.filter(tipo_pago=est_refrendopg,boleta=boleta).order_by("fecha_vencimiento_real")

				fecha_vencimiento=fe_ve["fecha_vencimiento_real__max"]
			else:
				fecha_vencimiento=boleta.fecha_vencimiento_real	
		except:
			fecha_vencimiento=boleta.fecha_vencimiento_real

	#boleta activa
	if boleta.estatus.id==1:
		if boleta.plazo.id==2:#semanal		
			#la boleta esta activa y es plazo semanal.
			#obtenemos todos los pagos tipo refrendo que no ha sido pagados.
			pagos_t_refrendo=Pagos.objects.filter(tipo_pago=est_refrendo,pagado="N",boleta=boleta).order_by("id")

			fec_boleta=datetime.combine(boleta.fecha,time.min)

			if fec_boleta==hoy:
				dias = timedelta(days=7)	
			else:
				dias = timedelta(days=6)	
			
			pag=Pagos.objects.filter(boleta=boleta,tipo_pago=est_refrendo,pagado="N")
			
			pag_actual=None
			for p in pag:
				fecha_i=datetime.combine(p.fecha_vencimiento-dias, time.min)                
				if p.fecha_vencimiento>=hoy and fecha_i<= hoy:
					#este es el pago que esta corriendo actualmente.
					pag_actual=p

			mutuo=boleta.mutuo

			fecha_vencimiento_real=fecha_vencimiento

			refrendo_pendiente=fn_calcula_saldo_refrendo(boleta,hoy)

			pag_ac=0
			#marcamos los pagos afectados como pagados.
			for pt in pagos_t_refrendo:

				if int(importe_abono)>=pt.importe and int(pag_ac)==0 and refrendo_pendiente>0:
					
					pt.pagado="S"
					pt.fecha_pago=timezone.now()
					pt.save()


					#creamos la relacion entre el abono y los pagos
					rel=Rel_Abono_Pago()
					rel.abono=abono
					rel.pago=pt
					rel.save()

					#por cada pago tipo refrendo pagado, generamos uno nuevo.
					dias = timedelta(days=7)	
					
					
					fecha_vencimiento=datetime.combine(fecha_vencimiento_real+dias, time.min)
				
					fecha_vencimiento_real=fecha_vencimiento

					fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

					
					pgo=Pagos()					
					pgo.tipo_pago=pt.tipo_pago
					pgo.boleta=pt.boleta
					pgo.fecha_vencimiento=fecha_vencimiento
					pgo.almacenaje=pt.almacenaje
					pgo.interes=pt.interes
					pgo.iva=pt.iva
					pgo.importe=pt.importe
					pgo.vencido="N"
					pgo.pagado="N"
					pgo.fecha_vencimiento_real=fecha_vencimiento_real
					pgo.save()
					importe_abono=int(importe_abono)-int(pt.importe)#disminuimos el saldo del importe abonado
					
						
					if pag_actual==pt:
						pag_ac=1



				

			num_pagos_no_vencidos=int(Pagos.objects.filter(vencido="N",pagado='N',tipo_pago=est_refrendo,boleta=boleta).count())



			
			#si el importe del abono es mayor a cero
			#y el numero de abonos no vencidos es 4
			# y no estamos en el periodo de algun refrendo no vencido.
			# abonamos al mutuo
			if int(importe_abono)>0 and (int(num_pagos_no_vencidos))==4 :
		
				mutuo=boleta.mutuo

				mutuo=int(mutuo)-int(importe_abono)

				rel_cap=Rel_Abono_Capital()
				rel_cap.boleta=boleta
				rel_cap.abono=abono
				rel_cap.importe=importe_abono
				rel_cap.capital_restante=mutuo
				rel_cap.save()

				#actualizamos el refrendo en base al nuevo mutuo
				ref=fn_calcula_refrendo(mutuo,boleta.tipo_producto.id)

				refrendo=math.ceil((ref[0]["refrendo"])/4)
				almacenaje=ref[0]["almacenaje"]/4
				interes=ref[0]["interes"]/4
				iva=ref[0]["iva"]/4

				#buscamos los abonos no pagados y no vencidos para actualizar su importe en base al nuevo mutuo
				pagos_t=Pagos.objects.filter(pagado="N",tipo_pago=est_refrendo,boleta=boleta,vencido="N").order_by("id")

				#actualizamos el importe de los pagos con el nuevo refrendo.
				for pt in pagos_t:
					if mutuo!=0:
						pt.importe=refrendo
						pt.almacenaje=almacenaje
						pt.interes=interes
						pt.iva=iva
						pt.save()
					else:
						pt.delete()
						#marcamos la boleeta como desempeñada.
						desempenada=Estatus_Boleta.objects.get(id=4)
						boleta.estatus=desempenada
						boleta.mutuo=0
						boleta.refrendo=0
						boleta.save()

			#actualizamos la fecha de vencimiento de la boleta.
			boleta.fecha_vencimiento=fecha_vencimiento
			boleta.fecha_vencimiento_real=fecha_vencimiento_real
			boleta.mutuo=mutuo
			boleta.save()
		else:#mensual
			#la boleta esta activa y es plazo mensual.						



			if int(recursivo)==1:
				#cuando es recursiva es que se trata de una boleta vencida, por lo tanto sus pagos tiporefrendo estan vencidos pero debe haber uno sin pagar
				pagos_t=Pagos.objects.get(boleta=boleta,tipo_pago=est_refrendo,pagado="N")
				fec_aux=hoy
			else:
				#como la boleta esta activa y es plazo mensual, solo debe tener un pago mensual vigente y sin pagar
				pagos_t=Pagos.objects.get(boleta=boleta,tipo_pago=est_refrendo,vencido="N",pagado="N")

				fec_aux=datetime.combine(fn_add_months(pagos_t.fecha_vencimiento,-1), time.min)	

			#si tiene mas de 1 pago no vencido, es que se pago el mes aque esta corriendo actualmetne y se genero uno nuevo
			# por lo tanto, ya no afecta a pagos, afecta a capital.
			cont_pagos_vencidos=Pagos.objects.filter(boleta=boleta,tipo_pago=est_refrendo,vencido="N").count()

			if (int(cont_pagos_vencidos)==1 or int(recursivo)==1) and (fec_aux<=hoy):

				#marcamos el pago como pagado.
				pagos_t.pagado="S"
				pagos_t.fecha_pago=timezone.now()
				pagos_t.save()


				#creamos la relacion entre el abono y los pagos
				rel=Rel_Abono_Pago()
				rel.abono=abono
				rel.pago=pagos_t
				rel.save()

				cont_ref=Pagos.objects.filter(boleta=boleta,tipo_pago=est_refrendo).count()
				cont_refpg=Pagos.objects.filter(boleta=boleta,tipo_pago=est_refrendopg).count()

				meses=int(cont_ref)+int(cont_refpg)+1


				#como ya se pago el refrendo actual, se genera un nuevo pago tipo refrendo.
				fecha_vencimiento=datetime.combine(fn_add_months(boleta.fecha,meses), time.min)	

				#validamos que la fecha de vencimiento no sea de azueto
				fecha_vencimiento=fn_fecha_vencimiento_valida(fecha_vencimiento)

				npt=Pagos()			
				npt.tipo_pago=pagos_t.tipo_pago
				npt.boleta=pagos_t.boleta
				npt.fecha_vencimiento=fecha_vencimiento
				npt.almacenaje=pagos_t.almacenaje
				npt.interes=pagos_t.interes
				npt.iva=pagos_t.iva
				npt.importe=pagos_t.importe
				npt.vencido="N"
				npt.pagado="N"
				npt.save()

				importe_abono=int(importe_abono)-int(pagos_t.importe)#disminuimos el saldo del importe abonado

			num_pagos_no_pagados=int(Pagos.objects.filter(boleta=boleta,pagado="N",tipo_pago=est_refrendo).count())

			#si entramos ene sesta condicion es porque estamos en el periodo de un refrendo PG
			if fec_aux>=hoy:
				num_pagos_no_pagados=num_pagos_no_pagados+1

			mutuo=boleta.mutuo			
			#si es mayor a cero
			#y el num de pagos no pagados es 2 , abonamos a capital.
			#if (int(importe_abono)>0 and (int(num_pagos_no_vencidos)==2) or (int(num_pagos_no_vencidos)==1 and int(recursivo)!=0)):			
			if (int(importe_abono)>0 and (int(num_pagos_no_pagados)==2) or (int(num_pagos_no_pagados)==1 and int(recursivo)!=0)):

				mutuo=int(mutuo)-int(importe_abono)
				
				
				

				rel_cap=Rel_Abono_Capital()
				rel_cap.boleta=boleta
				rel_cap.abono=abono
				rel_cap.importe=importe_abono
				rel_cap.capital_restante=mutuo
				rel_cap.save()


				#actualizamos el refrendo en base al nuevo mutuo
				ref=fn_calcula_refrendo(mutuo,boleta.tipo_producto.id)

				refrendo=math.ceil((ref[0]["refrendo"]))
				almacenaje=ref[0]["almacenaje"]
				interes=ref[0]["interes"]
				iva=ref[0]["iva"]

				npt=Pagos.objects.get(boleta=boleta,vencido="N",pagado="N",tipo_pago=est_refrendo)

				#si el mutuo es mayor a cero, actualizamos el importe de los pagos tipo refrendo
				if mutuo!=0:

					npt.importe=refrendo
					npt.almacenaje=almacenaje
					npt.interes=interes
					npt.iva=iva
					npt.save()
					
				else:# si el mutuo es cero, borramos el pago recien generado.
					npt.delete()
					desempenada=Estatus_Boleta.objects.get(id=4)
					boleta.estatus=desempenada
					boleta.mutuo=0
					boleta.refrendo=0
					boleta.save()
					#pagos_t.delete()
			#actualizamos la fecha de vencimiento de la boleta.
			boleta.fecha_vencimiento=fecha_vencimiento
			boleta.mutuo=mutuo
			boleta.save()
	else:#boleta vencida
		est_refrendo=Tipo_Pago.objects.get(id=1)
		est_comisionpg=Tipo_Pago.objects.get(id=2)
		est_refrendopg=Tipo_Pago.objects.get(id=3)

		#todos los pagos comision Pg deben ser cubiertos 
		pagos_comisionpg=Pagos.objects.filter(boleta=boleta,tipo_pago=est_comisionpg,pagado="N")
		for pcg in pagos_comisionpg:
			pcg.pagado="S"
			pcg.fecha_pago=timezone.now()
			pcg.save()

			#creamos la relacion entre el abono y los pagos
			rel=Rel_Abono_Pago()
			rel.abono=abono
			rel.pago=pcg
			rel.save()

			importe_abono=int(importe_abono)-int(pcg.importe)#disminuimos el saldo del importe abonado

		
		fv_final=boleta.fecha_vencimiento

		#todos los pagos comision Pg deben ser cubiertos 
		pagos_refrendopg=Pagos.objects.filter(boleta=boleta,tipo_pago=est_refrendopg,pagado="N")
		for prg in pagos_refrendopg:
			prg.pagado="S"
			prg.fecha_pago=timezone.now()
			prg.save()


			#creamos la relacion entre el abono y los pagos
			rel=Rel_Abono_Pago()
			rel.abono=abono
			rel.pago=prg
			rel.save()
			
			importe_abono=int(importe_abono)-int(prg.importe)#disminuimos el saldo del importe abonado


			#calculamos la nueva fecha de vencimiento
			#se toma la mas alta fecha devencimiento de Refrendo Pg
			if prg.fecha_vencimiento>fv_final:
				fv_final=prg.fecha_vencimiento

		boleta.fecha_vencimiento=fv_final
		boleta.save()

		rel_abono=Rel_Abono_Pago.objects.filter(abono=abono).order_by("id")

		#como al afectar pagos, primero afecta a refrendos pg, y posterior mente a refrendos,
		#en este ciclo reajustamos la forma en que afecto para que primero afecte a los refrendos y despues a los refrendos pg
  		#si nando comenta que srequiere que primero se afecten a los refrendos pg, solo hay qu quitar este ciclo.

		for x in rel_abono:
			if x.pago.tipo_pago.id==3:#buscamos los refrendos Pg que afecto
				paux=Pagos.objects.filter(boleta=boleta,pagado="N",tipo_pago=est_refrendo).order_by("fecha_vencimiento")#los refredos  que no han sido pagados.
				c_ont=0
				for y in paux:
					if c_ont==0:#para qe soloa afecte a un pago
						y.pagado="S"
						y.fecha_pago=x.pago.fecha_pago
						y.save()

						#marcamos el refrendo pg como no pagado
						x.pago.pagado="N"
						x.pago.fecha_pago=None
						x.pago.tipo_pago=y.tipo_pago
						x.pago.save()

						#cambiamos el pago al que afecto
						x.pago=y
						x.save()
					c_ont=1

		if boleta.fecha_vencimiento>=hoy:
			abierta=Estatus_Boleta.objects.get(id=1)
			boleta.estatus=abierta
			boleta.save()

		if importe_abono>0:
			#recursividad para acceder al algoritmo de una boleta activa.
			fn_aplica_refrendo(usuario,importe_abono,caja,boleta,1,abono)

	return 1





	


#funcion para generar folio de movimiento
def fn_folios(tipo_movimiento,sucursal):
	try:
		cf=Control_Folios.objects.get(tipo_movimiento=tipo_movimiento,sucursal=sucursal)
		folio=cf.folio+1
		cf.folio=folio
		cf.save()		
	except:
		#si no existe registro, crea uno
		Control_Folios.objects.create(tipo_movimiento=tipo_movimiento,sucursal=sucursal,folio=1)
		cf=Control_Folios.objects.get(tipo_movimiento=tipo_movimiento,sucursal=sucursal)
		folio=cf.folio
	return folio


def fn_str_clave(id):
	if len(str(id))==1:
		return '000000'+str(id)
	if len(str(id))==2:
		return '00000'+str(id)
	if len(str(id))==3:
		return '0000'+str(id)
	if len(str(id))==4:
		return '000'+str(id)
	if len(str(id))==5:
		return '00'+str(id)
	if len(str(id))==6:
		return '0'+str(id)
	if len(str(id))==7:
		return str(id)


def fn_envia_mail(cad,asunto,destinatario):

	html="<html><head></head><body>"
	html=html+cad		
	html=html+"</body></html>"


	html = html.replace("\xa1", "")
	html = html.replace("\xbf", "")
	html = html.replace("\xd1", "N")
	html = html.replace("\xdc", "U")
	html = html.replace("\xf1", "n")
	html = html.replace("\x0a", "\n")

	html = html.replace("\xe1", "a")		
	html = html.replace("\xe9", "e")		
	html = html.replace("\xed", "i")		
	html = html.replace("\xf3", "o")				
	html = html.replace("\xfa", "u")


	html = html.replace("\xc1", "A")		
	html = html.replace("\xc9", "E")		
	html = html.replace("\xcd", "I")		
	html = html.replace("\xd3", "O")				
	html = html.replace("\xda", "U")
	server = smtplib.SMTP('smtp.gmail.com:587')
	msg = email.message.Message()
	msg['Subject'] = asunto
	msg['From']=settings.EMAIL_HOST_USER
	msg['To']=destinatario
	password = settings.EMAIL_HOST_PASSWORD
	print(password)
	msg.add_header('Content-Type', 'text/html')
	msg.set_payload(html)		
	s = smtplib.SMTP('smtp.gmail.com:587')
	s.starttls()		
	# Login Credentials for sending the mail
	s.login(msg['From'], password)		
	s.sendmail(msg['From'], [msg['To']], msg.as_string())
	return 0

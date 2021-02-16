from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.pagesizes import A4
from django.conf import settings
from empenos.models import *
from django.db.models import Sum
import math
import requests
IP_LOCAL = settings.IP_LOCAL
LOCALHOST=settings.LOCALHOST
from datetime import datetime,date
import json
def imprime_corte_caja(request,id):
	hoy = date.today()
	txt_hoy = hoy.strftime("%Y-%m-%d")
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename=hello.pdf'
	buffer=BytesIO()


	try:
		obj = Cajas.objects.get(id = id)
	except Exception as e:
		print(e)
		return response 

	r = requests.get(settings.IP_LOCAL + '/empenos/api_consulta_corte_caja/?id_sucursal='+ str(obj.sucursal.id) +'&caja=A&fecha=' +  obj.fecha.strftime('%Y-%m-%d') + '&usuario=' + str(obj.sucursal.usuario_virtual.username))
	
	caja = r.json()	

	try:
		#si no encontramo la caja con el usuario virtual, buscamos con el usuario que qaperturo		
		if int(caja[0]["estatus"]) == 0:			
			r = requests.get(settings.IP_LOCAL + '/empenos/api_consulta_corte_caja/?id_sucursal='+ str(obj.sucursal.id) +'&caja=A&fecha=' +  obj.fecha.strftime('%Y-%m-%d') + '&usuario=' + str(obj.usuario.username))		
	except:
		pass

	caja = r.json()

	

	p=canvas.Canvas(buffer,pagesize=A4)

	p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 730,200, 60)

	p.setFont("Helvetica-Bold",15)

	p.drawString(400,750, "Folio: " + str(obj.folio))	

	p.setFont("Helvetica-Bold",10)
	p.drawString(55,700, "Fecha apertura: " + obj.fecha.strftime('%Y-%m-%d %H:%M:%S'))	
	p.drawString(55,680, "Fecha cierre: " + obj.fecha_cierre.strftime('%Y-%m-%d %H:%M:%S'))	
	if obj.usuario_real_abre_caja == None:
		p.drawString(55,660, "Usuario apertura: " + obj.usuario.username + ":- " + obj.usuario.first_name + " " + obj.usuario.last_name)
	else:
		p.drawString(55,660, "Usuario apertura: " + obj.usuario_real_abre_caja.username + ":- " + obj.usuario_real_abre_caja.first_name + " " + obj.usuario_real_abre_caja.last_name)
	p.drawString(55,640, "Usuario cierra: " + obj.user_cierra_caja.username + ":- " + obj.user_cierra_caja.first_name + " " + obj.user_cierra_caja.last_name)	
	p.drawString(55,620, "Sucursal: " + obj.sucursal.sucursal)
	p.drawString(55,600, "Comprobante corte de caja")


	row_act = 580
	row_size = 20

	#cuadro encabezado
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)

	p.drawString(60,row_act+5,"Ingreso teórico")
	p.drawString(310,row_act+5,"Real")
	###########################################################################
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########
	p.drawString(60,row_act+5,"Descripción")
	p.drawString(150,row_act+5,"# movs")
	p.drawString(210,row_act+5,"Importe")
	#########
	p.drawString(310,row_act+5,"Denominación")
	p.drawString(500,row_act+5,"Cantidad")

	###########################################################################
	p.setFont("Helvetica",10)
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########
	p.drawString(60,row_act+5,"Fondo inicial")
	p.drawString(150,row_act+5,"1")
	fondo_inicial = "{:0,.2f}".format(obj.importe)
	p.drawString(210,row_act+5,"$" + fondo_inicial)
	#########
	p.drawString(310,row_act+5,"1 Peso")
	p.drawString(500,row_act+5,str(caja[1]["pesos_1"]))

	###########################################################################
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########
	p.drawString(60,row_act+5,"Otros ingresos")
	p.drawString(150,row_act+5,str(caja[0]["cont_otros_ingresos"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_otros_ingresos"]))
	p.drawString(210,row_act+5,"$" + otros_ingresos)
	#########
	p.drawString(310,row_act+5,"2 Pesos")
	p.drawString(500,row_act+5,str(caja[1]["pesos_2"]))
	###########################################################################
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########
	p.drawString(60,row_act+5,"Refrendos")
	p.drawString(150,row_act+5,str(caja[0]["cont_refrendos"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_importe_refrendo"]))
	p.drawString(210,row_act+5,"$" + otros_ingresos)
	#########
	p.drawString(310,row_act+5,"5 Pesos")
	p.drawString(500,row_act+5,str(caja[1]["pesos_5"]))
	###########################################################################
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########
	p.drawString(60,row_act+5,"Comisiónes PG")
	p.drawString(150,row_act+5,str(caja[0]["cont_com_pg"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_comisiones_pg"]))
	p.drawString(210,row_act+5,"$" + otros_ingresos)
	#########
	p.drawString(310,row_act+5,"10 Pesos")
	p.drawString(500,row_act+5,str(caja[1]["pesos_10"]))
	###########################################################################
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########
	p.drawString(60,row_act+5,"Pago capital")
	p.drawString(150,row_act+5,str(caja[0]["cont_pc"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_pago_capital"]))
	p.drawString(210,row_act+5,"$" + otros_ingresos)
	#########
	p.drawString(310,row_act+5,"20 Pesos")
	p.drawString(500,row_act+5,str(caja[1]["pesos_20"]))
	###########################################################################
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########
	p.drawString(60,row_act+5,"Desempeño")
	p.drawString(150,row_act+5,str(caja[0]["cont_desemp"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_importe_desemp"]))
	p.drawString(210,row_act+5,"$" + otros_ingresos)
	#########
	p.drawString(310,row_act+5,"50 Pesos")
	p.drawString(500,row_act+5,str(caja[1]["pesos_50"]))

	###########################################################################
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########
	p.drawString(60,row_act+5,"Reimp. Boleta")
	p.drawString(150,row_act+5,str(caja[0]["cont_rebol"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_importe_rebol"]))
	p.drawString(210,row_act+5,"$" + otros_ingresos)
	#########
	p.drawString(310,row_act+5,"100 Pesos")
	p.drawString(500,row_act+5,str(caja[1]["pesos_100"]))
	###########################################################################

	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########
	p.drawString(60,row_act+5,"Ventas")
	p.drawString(150,row_act+5,str(caja[0]["cont_ventas"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_importe_ventas"]))
	p.drawString(210,row_act+5,"$" + otros_ingresos)
	#########
	p.drawString(310,row_act+5,"200 Pesos")
	p.drawString(500,row_act+5,str(caja[1]["pesos_200"]))


	###########################################################################
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########
	p.drawString(60,row_act+5,"Abono apartado")
	p.drawString(150,row_act+5,str(caja[0]["cont_ab_apartado"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_importe_apartado"]))
	p.drawString(210,row_act+5,"$" + otros_ingresos)
	#########
	p.drawString(310,row_act+5,"500 Pesos")
	p.drawString(500,row_act+5,str(caja[1]["pesos_500"]))

	###########################################################################
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	p.setFont("Helvetica-Bold",10)
	#########
	p.drawString(60,row_act+5,"Salidas teórico")	
	p.setFont("Helvetica",10)
	#########
	p.drawString(310,row_act+5,"1000 Pesos")
	p.drawString(500,row_act+5,str(caja[1]["pesos_1000"]))

	###########################################################################
	
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########
	p.drawString(60,row_act+5,"Retiro de caja")
	p.drawString(150,row_act+5,str(caja[0]["cont_retiros"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_retiros"]))
	p.drawString(210,row_act+5,"$" + otros_ingresos)
	#########
	#p.drawString(310,row_act+5,"500 Pesos")
	#p.drawString(500,row_act+5,str(caja[1]["pesos_500"]))


	###########################################################################

	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########
	p.drawString(60,row_act+5,"Empeños")
	p.drawString(150,row_act+5,str(caja[0]["cont_empenos"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_empenos"]))
	p.drawString(210,row_act+5,"$" + otros_ingresos)
	#########
	#p.drawString(310,row_act+5,"Total")
	#p.drawString(500,row_act+5,str(caja[1]["pesos_500"]))


	###########################################################################
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########
	p.setFont("Helvetica-Bold",10)
	p.drawString(60,row_act+5,"Total teórico")	
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_total_efectivo"]))
	p.drawString(210,row_act+5,"$" + otros_ingresos)
	#########
	p.drawString(310,row_act+5,"Total real")
	total_real = "{:0,.2f}".format(obj.real_efectivo)
	p.drawString(450,row_act+5,"$" + total_real)

	###########################################################################
	row_act -= row_size
	p.line(55,row_act,295,row_act)
	p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act+20)
	p.line(295,row_act,295,row_act+20)
	p.line(305,row_act,305,row_act+20)
	p.line(545,row_act,545,row_act+20)
	#########


	
	p.drawString(310,row_act+5,"Diferencia")
	diferencia = "{:0,.2f}".format(obj.diferencia)
	p.drawString(450,row_act+5,"$" + diferencia)
	###########################################################################
	row_act -= row_size
	p.line(55,row_act,545,row_act)
	#p.line(305,row_act,545,row_act)
	p.line(55,row_act,55,row_act-100)
	#p.line(295,row_act,295,row_act-20)
	#p.line(305,row_act,305,row_act-20)
	p.line(545,row_act,545,row_act-100)

	row_act -= row_size
	p.drawString(60,row_act+5,"Comentarios:")
	p.setFont("Helvetica",8)
	row_act -= row_size

	p.drawString(60,row_act+5,obj.comentario.upper()[0:100])
	row_act -= row_size
	p.drawString(60,row_act+5,obj.comentario.upper()[100:200])
	row_act -= row_size
	p.drawString(60,row_act+5,obj.comentario.upper()[200:300])
	row_act -= row_size	
	p.drawString(60,row_act+5,obj.comentario.upper()[300:400])
	p.line(55,row_act,545,row_act)
	




	p.save()
	pdf=buffer.getvalue()
	buffer.close()
	response.write(pdf)
	return response



def rep_cajas_abiertas(obj_reporte,fecha_inicial,fecha_final,request,sucursal):
	hoy = date.today()
	txt_hoy = hoy.strftime("%Y-%m-%d")
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename=hello.pdf'
	buffer=BytesIO()

	p=canvas.Canvas(buffer,pagesize=(landscape(letter)))

	num_paginas = math.ceil(float(obj_reporte.count())/float(24))

	row_act = 480
	row_size = 20

	cont_pag = 1
	cont = 0
	for o in obj_reporte:
		
		if cont == 20 or cont == 0:
			
			p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 530,200, 60)
			p.drawString(630,560,"Pag. "+str(cont_pag) + " de " + str(int(num_paginas)))

			p.setFont("Helvetica-Bold",10)
			p.drawString(300,560, "Fecha de generación: " + txt_hoy)	
			p.drawString(300,540, "Usuario: " + request.user.username + ":- " + request.user.first_name + " " + request.user.last_name)
			p.drawString(300,520, "Sucursal: " + sucursal)
			p.drawString(300,500, "Reporte de cajas abiertas del día " + fecha_inicial + ' al ' + fecha_final )

			row_act = 480
			row_size = 20
			p.line(55,row_act,545,row_act)
			row_act = row_act - row_size
			p.drawString(60,row_act+5,"Folio")
			p.drawString(100,row_act+5,"Usr Apert")
			p.drawString(160,row_act+5,"Importe Ap")
			p.drawString(230,row_act+5,"Usr Cierre")
			p.drawString(290,row_act+5,"Teor Cierre")
			p.drawString(360,row_act+5,"Real cierre")			
			p.drawString(430,row_act+5,"Difrencia")
			p.drawString(500,row_act+5,"Fecha Apertura")
			p.drawString(615,row_act+5,"Fecha Cierre")

			p.line(55,row_act,55,row_act+20)
			p.line(95,row_act,95,row_act+20)
			p.line(155,row_act,155,row_act+20)
			p.line(225,row_act,225,row_act+20)#usuario cierre

			p.line(285,row_act,285,row_act+20)#importe cierra

			p.line(355,row_act,355,row_act+20)#diferencia

			p.line(425,row_act,425,row_act+20)
			p.line(495,row_act,495,row_act+20)
			p.line(610,row_act,610,row_act+20)
			p.line(725,row_act,725,row_act+20)

			p.line(55,row_act,725,row_act)
			p.line(55,row_act+20,725,row_act+20)

			cont = 1
			cont_pag += 1
			p.line(55,row_act,545,row_act)
			row_act = row_act - row_size

		cont += 1
	
		p.line(55,row_act,55,row_act+20)
		p.line(95,row_act,95,row_act+20)
		p.line(155,row_act,155,row_act+20)
		p.line(225,row_act,225,row_act+20)#usuario cierre

		p.line(285,row_act,285,row_act+20)#teorico cierre

		p.line(355,row_act,355,row_act+20)#real cierre

		p.line(425,row_act,425,row_act+20)#diferencia

		p.line(495,row_act,495,row_act+20)
		p.line(610,row_act,610,row_act+20)
		p.line(725,row_act,725,row_act+20)

		p.line(55,row_act,725,row_act)

		p.setFont("Helvetica",7)
		p.drawString(60,row_act+5,o.folio)

		txt_username = ""
		if o.usuario_real_abre_caja == None:
			txt_username = o.usuario.username
		else:
			txt_username = o.usuario_real_abre_caja.username

		p.drawString(100,row_act+5,txt_username)

		importe_apertura = "{:0,.2f}".format(o.importe)
		p.drawString(160,row_act+5,"$"+importe_apertura)

		if o.user_cierra_caja != None:
			p.drawString(230,row_act+5,o.user_cierra_caja.username)

		teorico_efectivo = "{:0,.2f}".format(o.teorico_efectivo)
		p.drawString(290,row_act+5,"$"+teorico_efectivo)

		real_efectivo = "{:0,.2f}".format(o.real_efectivo)
		p.drawString(360,row_act+5,"$"+real_efectivo)

		diferencia = "{:0,.2f}".format(o.diferencia)
		p.drawString(430,row_act+5,"$"+diferencia)

		fecha_apertura = datetime.strftime(o.fecha,'%Y-%m-%d %H:%M:%S')
		p.drawString(500,row_act+5,str(fecha_apertura))
		if o.fecha_cierre != None:
			fecha_cierre = datetime.strftime(o.fecha_cierre,'%Y-%m-%d %H:%M:%S')
			p.drawString(615,row_act+5,str(fecha_cierre))

		row_act = row_act - row_size

		if cont == 20:
			p.showPage()

	p.save()
	pdf=buffer.getvalue()
	buffer.close()
	response.write(pdf)
	return response


def rep_ingresos_efectivo(obj_reporte,fecha_inicial,fecha_final,request,sucursal):
	hoy = date.today()
	txt_hoy = hoy.strftime("%Y-%m-%d")
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename=hello.pdf'
	buffer=BytesIO()

	p=canvas.Canvas(buffer,pagesize=A4)

	num_paginas = math.ceil(float(obj_reporte.count())/float(24))






	row_act = 620
	row_size = 20

	cont_pag = 1
	cont = 0
	for o in obj_reporte:
		
		if cont == 25 or cont == 0:
			
			p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 730,200, 60)
			p.drawString(460,730,"Pag. "+str(cont_pag) + " de " + str(int(num_paginas)))

			p.setFont("Helvetica-Bold",10)
			p.drawString(55,700, "Fecha de generación: " + txt_hoy)	
			p.drawString(55,680, "Usuario: " + request.user.username + ":- " + request.user.first_name + " " + request.user.last_name)
			p.drawString(55,660, "Sucursal: " + sucursal)
			p.drawString(55,640, "Reporte de ingreso de efectivo del día " + fecha_inicial + ' al ' + fecha_final )

			row_act = 620
			row_size = 20
			p.line(55,row_act,545,row_act)
			row_act = row_act - row_size
			p.drawString(60,row_act+5,"Folio")
			p.drawString(100,row_act+5,"Usuario")
			p.drawString(160,row_act+5,"Importe")
			p.drawString(230,row_act+5,"Comentarios")
			p.drawString(460,row_act+5,"Fecha")
			p.drawString(510,row_act+5,"Activo")

			p.line(55,row_act,55,row_act+20)
			p.line(95,row_act,95,row_act+20)
			p.line(155,row_act,155,row_act+20)
			p.line(225,row_act,225,row_act+20)
			p.line(455,row_act,455,row_act+20)
			p.line(505,row_act,505,row_act+20)
			p.line(545,row_act,545,row_act+20)
			p.line(55,row_act,545,row_act)

			cont = 1
			cont_pag += 1
			p.line(55,row_act,545,row_act)
			row_act = row_act - row_size

		cont += 1
		p.line(55,row_act,55,row_act+20)
		p.line(95,row_act,95,row_act+20)
		p.line(155,row_act,155,row_act+20)
		p.line(225,row_act,225,row_act+20)
		p.line(455,row_act,455,row_act+20)
		p.line(505,row_act,505,row_act+20)
		p.line(545,row_act,545,row_act+20)
		p.line(55,row_act,545,row_act)

		p.setFont("Helvetica",7)
		p.drawString(60,row_act+5,o.folio)
		p.drawString(100,row_act+5,o.usuario.username)
		
		
		importe = "{:0,.2f}".format(o.importe)
		p.drawString(160,row_act+5,"$"+importe)
		
		p.drawString(230,row_act+5,o.comentario[0:50])
		fecha = datetime.strftime(o.fecha,'%Y-%m-%d')
		p.drawString(460,row_act+5,fecha)
		if o.activo == "1":
			activo = "SI"
		else:
			activo = "NO"
		p.drawString(510,row_act+5,activo)

		row_act = row_act - row_size

		if cont == 25:
			p.showPage()
	p.setFont("Helvetica-Bold",10)

	p.line(55,row_act,55,row_act+20)
	p.drawString(60,row_act+5,"Total")
	p.line(155,row_act,155,row_act+20)
	oi = obj_reporte.aggregate(Sum("importe"))
	importe = 0
	if oi["importe__sum"] != None:
		importe = oi["importe__sum"]

	importe = "{:0,.2f}".format(importe)
	p.drawString(160,row_act+5,"$"+str(importe))
	
	
	p.line(545,row_act,545,row_act+20)
	p.line(55,row_act,545,row_act)
			
			
			
	

	p.save()
	pdf=buffer.getvalue()
	buffer.close()
	response.write(pdf)
	return response


def imprime_comprobante_ingreso(request,id):
	hoy = date.today()
	txt_hoy = hoy.strftime("%Y-%m-%d")
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename=hello.pdf'
	buffer=BytesIO()

	try:
		obj = Otros_Ingresos.objects.get(id = id)
	except Exception as e:
		print(e)
		return response 

	p=canvas.Canvas(buffer,pagesize=A4)

	p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 730,200, 60)

	p.setFont("Helvetica-Bold",15)

	p.drawString(400,750, "Folio retiro: " + str(obj.folio))	

	p.setFont("Helvetica-Bold",10)
	p.drawString(55,700, "Fecha: " + txt_hoy)	
	p.drawString(55,680, "Usuario: " + request.user.username + ":- " + request.user.first_name + " " + request.user.last_name)
	p.drawString(55,660, "Sucursal: " + obj.sucursal.sucursal)
	p.drawString(55,640, "Comprobante de retiro de efectivo ")

	row_act = 620
	row_size = 20

	p.line(55,row_act,545,row_act)
	row_act = row_act - row_size
	p.drawString(60,row_act + 5,"Importe")
	
	importe = "{:0,.2f}".format(float(obj.importe))

	p.drawString(155,row_act + 5, "$" + importe)
	p.line(55,row_act,545,row_act)
	row_act = row_act - row_size
	

	
	p.drawString(60,row_act + 5,"Comentarios")
	p.drawString(155,row_act + 5,obj.comentario)
	p.line(55,row_act,545,row_act)
	

	#p.drawString(60,row_act + 5,"Comentarios")

	#p.setFont("Helvetica-Bold",10)	
	#p.drawString(155,row_act + 5,obj.comentario)

	#p.setFont("Helvetica-Bold",10)
	#p.line(55,row_act,545,row_act)
	#row_act = row_act - row_size
	#p.drawString(60,row_act + 5,"Folio autorización")
	#p.drawString(155,row_act + 5,str(obj.token))
	#p.line(55,row_act,545,row_act)
	

	p.line(55,620,55,row_act)
	p.line(150,620,150,row_act )
	p.line(545,620,545,row_act )

	p.save()
	pdf=buffer.getvalue()
	buffer.close()
	response.write(pdf)
	return response

def imprime_comprobante_retiro(request,id):
	hoy = date.today()
	txt_hoy = hoy.strftime("%Y-%m-%d")
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename=hello.pdf'
	buffer=BytesIO()

	try:
		obj = Retiro_Efectivo.objects.get(id = id)
	except Exception as e:
		print(e)
		return response 

	p=canvas.Canvas(buffer,pagesize=A4)

	p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 730,200, 60)

	p.setFont("Helvetica-Bold",15)

	p.drawString(400,750, "Folio retiro: " + str(obj.folio))	

	p.setFont("Helvetica-Bold",10)
	p.drawString(55,700, "Fecha: " + txt_hoy)	
	p.drawString(55,680, "Usuario: " + request.user.username + ":- " + request.user.first_name + " " + request.user.last_name)
	p.drawString(55,660, "Sucursal: " + obj.sucursal.sucursal)
	p.drawString(55,640, "Comprobante de retiro de efectivo ")

	row_act = 620
	row_size = 20

	p.line(55,row_act,545,row_act)
	row_act = row_act - row_size
	p.drawString(60,row_act + 5,"Concepto de retiro")
	concepto = ""
	if obj.concepto != None:
		concepto = obj.concepto.concepto

	p.drawString(155,row_act + 5,concepto)
	p.line(55,row_act,545,row_act)
	row_act = row_act - row_size
	

	importe = "{:0,.2f}".format(float(obj.importe))
	p.drawString(60,row_act + 5,"Importe")
	p.drawString(155,row_act + 5,"$" + importe)
	p.line(55,row_act,545,row_act)
	row_act = row_act - row_size

	p.drawString(60,row_act + 5,"Comentarios")

	p.setFont("Helvetica-Bold",7)	
	p.drawString(155,row_act + 5,obj.comentario)

	p.setFont("Helvetica-Bold",10)
	p.line(55,row_act,545,row_act)
	row_act = row_act - row_size
	p.drawString(60,row_act + 5,"Folio autorización")
	p.drawString(155,row_act + 5,str(obj.token))
	p.line(55,row_act,545,row_act)
	

	p.line(55,620,55,row_act)
	p.line(150,620,150,row_act )
	p.line(545,620,545,row_act )

	p.save()
	pdf=buffer.getvalue()
	buffer.close()
	response.write(pdf)
	return response


def reporte_retiro_efectivo(obj_reporte,fecha_inicial,fecha_final,request,sucursal):
	hoy = date.today()
	txt_hoy = hoy.strftime("%Y-%m-%d")
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename=hello.pdf'
	buffer=BytesIO()

	p=canvas.Canvas(buffer,pagesize=A4)

	num_paginas = math.ceil(float(obj_reporte.count())/float(24))






	row_act = 620
	row_size = 20

	cont_pag = 1
	cont = 0
	for o in obj_reporte:
		
		if cont == 25 or cont == 0:
			
			p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 730,200, 60)
			p.drawString(460,730,"Pag. "+str(cont_pag) + " de " + str(int(num_paginas)))

			p.setFont("Helvetica-Bold",10)
			p.drawString(55,700, "Fecha de generación: " + txt_hoy)	
			p.drawString(55,680, "Usuario: " + request.user.username + ":- " + request.user.first_name + " " + request.user.last_name)
			p.drawString(55,660, "Sucursal: " + sucursal)
			p.drawString(55,640, "Reporte de retiro de efectivo del día " + fecha_inicial + ' al ' + fecha_final )

			row_act = 620
			row_size = 20
			p.line(55,row_act,545,row_act)
			row_act = row_act - row_size
			p.drawString(60,row_act+5,"Folio")
			p.drawString(100,row_act+5,"Usuario")
			p.drawString(160,row_act+5,"Importe")
			p.drawString(230,row_act+5,"Concepto")
			p.drawString(440,row_act+5,"Fecha")
			p.drawString(510,row_act+5,"Activo")

			p.line(55,row_act,55,row_act+20)
			p.line(95,row_act,95,row_act+20)
			p.line(155,row_act,155,row_act+20)
			p.line(225,row_act,225,row_act+20)
			p.line(435,row_act,435,row_act+20)
			p.line(505,row_act,505,row_act+20)
			p.line(545,row_act,545,row_act+20)
			p.line(55,row_act,545,row_act)

			cont = 1
			cont_pag += 1
			p.line(55,row_act,545,row_act)
			row_act = row_act - row_size

		cont += 1
		p.line(55,row_act,55,row_act+20)
		p.line(95,row_act,95,row_act+20)
		p.line(155,row_act,155,row_act+20)
		p.line(225,row_act,225,row_act+20)
		p.line(435,row_act,435,row_act+20)
		p.line(505,row_act,505,row_act+20)
		p.line(545,row_act,545,row_act+20)
		p.line(55,row_act,545,row_act)

		p.setFont("Helvetica",7)
		p.drawString(60,row_act+5,o.folio)
		p.drawString(100,row_act+5,o.usuario.username)
		
		
		importe = "{:0,.2f}".format(o.importe)
		p.drawString(160,row_act+5,"$"+importe)
		concepto = ""
		if o.concepto != None:
			concepto = o.concepto.concepto
		p.drawString(230,row_act+5,concepto)
		fecha = datetime.strftime(o.fecha,'%Y-%m-%d')
		p.drawString(440,row_act+5,fecha)
		if o.activo == "1":
			activo = "SI"
		else:
			activo = "NO"
		p.drawString(510,row_act+5,activo)

		row_act = row_act - row_size

		if cont == 25:
			p.showPage()
	p.setFont("Helvetica-Bold",10)

	p.line(55,row_act,55,row_act+20)
	p.drawString(60,row_act+5,"Total")
	p.line(155,row_act,155,row_act+20)
	oi = obj_reporte.aggregate(Sum("importe"))
	importe = 0
	if oi["importe__sum"] != None:
		importe = oi["importe__sum"]

	importe = "{:0,.2f}".format(importe)
	p.drawString(160,row_act+5,"$"+str(importe))
	
	
	p.line(545,row_act,545,row_act+20)
	p.line(55,row_act,545,row_act)
			
			
			
	

	p.save()
	pdf=buffer.getvalue()
	buffer.close()
	response.write(pdf)
	return response

def reporte_comparativo_carteras(dic,user,fecha_1,fecha_2,txt_sucursal):

	hoy = date.today()
	txt_hoy = hoy.strftime("%Y-%m-%d")
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename=hello.pdf'
	buffer=BytesIO()

	p=canvas.Canvas(buffer,pagesize=A4)

	p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 730,200, 60)

	p.setFont("Helvetica-Bold",10)
	p.drawString(55,700, "Fecha impresión: " + txt_hoy)	
	p.drawString(350,700, "Usuario imprime: " + user.username)


	p.drawString(55,680, "Sucursal (es): " + txt_sucursal)
	p.setFont("Helvetica-Bold",10)
	p.drawString(55,660, "Comparación del estatus de cartera del día " + fecha_2 + " contra el día " + fecha_1 )

	row_act = 640
	row_size = 20
	
	aux_r = row_act
	#dibujamos lineas verticales de la primera tabla
	p.line(55,row_act,545,row_act)

	row_act -= row_size
	
	p.drawString(60,row_act+5,"Cartera del día  " + fecha_1 )

	p.line(55,row_act,545,row_act)	

	row_act -= row_size


	p.line(55,row_act,545,row_act)	

	row_act -= row_size
		
	p.drawString(60,row_act+5,"Boleta activa")


	p.drawString(182,row_act+5,""+ dic["fecha_1"]["cont_activas"] )
	p.drawString(304,row_act+5,"$" + dic["fecha_1"]["mutuo_activo"] )
	p.drawString(426,row_act+5,"$" + dic["fecha_1"]["avaluo_activo"] )

	p.line(55,row_act,545,row_act)	

	row_act -= row_size

	
	p.drawString(60,row_act+5,"Boleta almoneda")
	p.drawString(182,row_act+5, dic["fecha_1"]["cont_almoneda"] )
	p.drawString(304,row_act+5,"$" + dic["fecha_1"]["mutuo_almoneda"] )
	p.drawString(426,row_act+5,"$" + dic["fecha_1"]["avaluo_almoneda"] )
	
	p.line(55,row_act,545,row_act)	

	row_act -= row_size

	p.drawString(60,row_act+5,"Boleta remate")
	p.drawString(182,row_act+5,dic["fecha_1"]["cont_remate"] )
	p.drawString(304,row_act+5,"$" + dic["fecha_1"]["mutuo_remate"] )
	p.drawString(426,row_act+5,"$" + dic["fecha_1"]["avaluo_remate"] )
	
	p.line(55,row_act,545,row_act)	

	row_act -= row_size

	p.drawString(60,row_act+5,"Total")
	
	p.drawString(182,row_act+5,dic["fecha_1"]["cont_total"] )
	p.drawString(304,row_act+5,"$" + dic["fecha_1"]["mutuo_total"] )
	p.drawString(426,row_act+5,"$" + dic["fecha_1"]["avaluo_total"] )

	p.line(55,row_act,545,row_act)	

	#dibujamos lineas horizontales de segundas tabla.
	p.line(55,aux_r,55,row_act)	
	p.line(177,aux_r-20,177,row_act)
	p.drawString(182,aux_r-35,"Cantidad")

	p.line(299,aux_r-20,299,row_act)	
	p.drawString(304,aux_r-35,"Importe mutuo")
	p.line(421,aux_r-20,421,row_act)	
	p.drawString(426,aux_r-35,"Importe Avaluo")	
	p.line(545,aux_r,545,row_act)	

	row_act -= row_size		
	row_act -= row_size		
	row_act -= row_size	


	aux_r = row_act
	#dibujamos lineas verticales de la segunda tabla
	p.line(55,row_act,545,row_act)

	row_act -= row_size
	
	p.drawString(60,row_act+5,"Cartera del día  " + fecha_2 )

	p.line(55,row_act,545,row_act)	

	row_act -= row_size


	p.line(55,row_act,545,row_act)	

	row_act -= row_size
		
	p.drawString(60,row_act+5,"Boleta activa")


	p.drawString(182,row_act+5,""+ dic["fecha_2"]["cont_activas"] )
	p.drawString(304,row_act+5,"$" + dic["fecha_2"]["mutuo_activo"] )
	p.drawString(426,row_act+5,"$" + dic["fecha_2"]["avaluo_activo"] )

	p.line(55,row_act,545,row_act)	

	row_act -= row_size

	
	p.drawString(60,row_act+5,"Boleta almoneda")
	p.drawString(182,row_act+5, dic["fecha_2"]["cont_almoneda"] )
	p.drawString(304,row_act+5,"$" + dic["fecha_2"]["mutuo_almoneda"] )
	p.drawString(426,row_act+5,"$" + dic["fecha_2"]["avaluo_almoneda"] )
	
	p.line(55,row_act,545,row_act)	

	row_act -= row_size

	p.drawString(60,row_act+5,"Boleta remate")
	p.drawString(182,row_act+5,dic["fecha_2"]["cont_remate"] )
	p.drawString(304,row_act+5,"$" + dic["fecha_2"]["mutuo_remate"] )
	p.drawString(426,row_act+5,"$" + dic["fecha_2"]["avaluo_remate"] )
	
	p.line(55,row_act,545,row_act)	

	row_act -= row_size

	p.drawString(60,row_act+5,"Total")
	
	p.drawString(182,row_act+5,dic["fecha_2"]["cont_total"] )
	p.drawString(304,row_act+5,"$" + dic["fecha_2"]["mutuo_total"] )
	p.drawString(426,row_act+5,"$" + dic["fecha_2"]["avaluo_total"] )

	p.line(55,row_act,545,row_act)

	#dibujamos lineas horizontales de las segunda tablas.
	p.line(55,aux_r,55,row_act)	
	p.line(177,aux_r-20,177,row_act)
	p.drawString(182,aux_r-35,"Cantidad")

	p.line(299,aux_r-20,299,row_act)	
	p.drawString(304,aux_r-35,"Importe mutuo")
	p.line(421,aux_r-20,421,row_act)	
	p.drawString(426,aux_r-35,"Importe Avaluo")	
	p.line(545,aux_r,545,row_act)	

	row_act -= row_size		
	row_act -= row_size		
	row_act -= row_size	

	aux_r = row_act
	#dibujamos lineas verticales de la segunda tabla
	p.line(55,row_act,545,row_act)

	row_act -= row_size
	
	p.drawString(60,row_act+5,"Crecimiento de cartera del " + fecha_1 + " al " + fecha_2)

	p.line(55,row_act,545,row_act)	

	row_act -= row_size


	p.line(55,row_act,545,row_act)	

	row_act -= row_size
		
	p.drawString(60,row_act+5,"Boleta activa")


	p.drawString(182,row_act+5,""+ dic["comparacion"]["cont_activas"] )
	p.drawString(304,row_act+5,"$" + dic["comparacion"]["mutuo_activo"] )
	p.drawString(426,row_act+5,"$" + dic["comparacion"]["avaluo_activo"] )

	p.line(55,row_act,545,row_act)	

	row_act -= row_size

	
	p.drawString(60,row_act+5,"Boleta almoneda")
	p.drawString(182,row_act+5, dic["comparacion"]["cont_almoneda"] )
	p.drawString(304,row_act+5,"$" + dic["comparacion"]["mutuo_almoneda"] )
	p.drawString(426,row_act+5,"$" + dic["comparacion"]["avaluo_almoneda"] )
	
	p.line(55,row_act,545,row_act)	

	row_act -= row_size

	p.drawString(60,row_act+5,"Boleta remate")
	p.drawString(182,row_act+5,dic["comparacion"]["cont_remate"] )
	p.drawString(304,row_act+5,"$" + dic["comparacion"]["mutuo_remate"] )
	p.drawString(426,row_act+5,"$" + dic["comparacion"]["avaluo_remate"] )
	
	p.line(55,row_act,545,row_act)	

	row_act -= row_size

	p.drawString(60,row_act+5,"Total")
	
	p.drawString(182,row_act+5,dic["comparacion"]["cont_total"] )
	p.drawString(304,row_act+5,"$" + dic["comparacion"]["mutuo_total"] )
	p.drawString(426,row_act+5,"$" + dic["comparacion"]["avaluo_total"] )

	p.line(55,row_act,545,row_act)	

	#dibujamos lineas horizontales de las segunda tablas.
	p.line(55,aux_r,55,row_act)	
	p.line(177,aux_r-20,177,row_act)
	p.drawString(182,aux_r-35,"Cantidad")

	p.line(299,aux_r-20,299,row_act)	
	p.drawString(304,aux_r-35,"Importe mutuo")
	p.line(421,aux_r-20,421,row_act)	
	p.drawString(426,aux_r-35,"Importe Avaluo")	
	p.line(545,aux_r,545,row_act)		
	p.save()
	pdf=buffer.getvalue()
	buffer.close()
	response.write(pdf)
	return response
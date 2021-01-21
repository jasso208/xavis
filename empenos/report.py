from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.pagesizes import A4
from django.conf import settings
from empenos.models import *
from django.db.models import Sum
import math
IP_LOCAL = settings.IP_LOCAL
LOCALHOST=settings.LOCALHOST
from datetime import datetime,date


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
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.pagesizes import A4
from django.conf import settings
from empenos.models import *
IP_LOCAL = settings.IP_LOCAL
LOCALHOST=settings.LOCALHOST
from datetime import datetime,date

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
	p.drawString(155,row_act + 5,obj.concepto.concepto)
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
	p.drawString(55,660, "Comparacion del estatus de cartera del día " + fecha_2 + " contra el día " + fecha_1 )

	row_act = 640
	row_size = 20
	
	aux_r = row_act
	#dibujamos lineas verticales de la primera tabla
	p.line(55,row_act,545,row_act)

	row_act -= row_size
	
	p.drawString(60,row_act+5,"Cartera del dia  " + fecha_1 )

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
	
	p.drawString(60,row_act+5,"Cartera del dia  " + fecha_2 )

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
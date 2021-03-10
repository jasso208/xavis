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


def rep_imprime_venta_piso(request,id_venta):
	print("entro")
	venta = Venta_Piso.objects.get(id = id_venta)
	hoy = date.today()
	txt_hoy = hoy.strftime("%Y-%m-%d")
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename=hello.pdf'
	buffer=BytesIO()

	pos_copia = 380

	p=canvas.Canvas(buffer,pagesize=(letter))


	p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 700,200, 60)

	#copia
	p.drawImage(settings.IP_LOCAL+'/static/img/logo.jpg', 55, 700 - pos_copia,200, 60)

	#cuadro 1] Informaciond de la empresa
	p.line(50,700,50,615)	
	p.line(50,700,280,700)
	p.line(280,700,280,615)	
	p.line(50,615,280,615)

	#copia
	#cuadro 1] Informaciond de la empresa
	p.line(50,700 - pos_copia,50,615- pos_copia)	
	p.line(50,700 - pos_copia,280,700 - pos_copia)
	p.line(280,700 - pos_copia,280,615- pos_copia)	
	p.line(50,615 - pos_copia, 280,615- pos_copia)



	

	p.setFont("Helvetica-Bold",7)
	p.drawString(55,690,"Empresa:")
	p.setFont("Helvetica",7)
	p.drawString(55,680,"   " + Empresa.objects.get(id = 1).nombre_empresa)
	p.setFont("Helvetica",7)
	p.drawString(55,670,"      "+Empresa.objects.get(id = 1).horario)
	p.setFont("Helvetica-Bold",7)
	p.drawString(55,650,"RFC:")
	p.setFont("Helvetica",7)
	p.drawString(75,650,Empresa.objects.get(id = 1).rfc)
	p.setFont("Helvetica-Bold",7)
	p.drawString(170,650,"Telefono:")
	p.setFont("Helvetica",7)
	p.drawString(210,650,venta.sucursal.telefono)

	p.setFont("Helvetica-Bold",7)
	p.drawString(55,640,"Dirección:")
	p.setFont("Helvetica",7)
	p.drawString(100,640,venta.sucursal.calle+' No. Int. '+str(venta.sucursal.numero_interior)+' No. ext. '+str(venta.sucursal.numero_exterior))
	p.setFont("Helvetica",7)
	p.drawString(55,630,' CP ' + str(venta.sucursal.codigo_postal) + ' ' + venta.sucursal.colonia + ', '+venta.sucursal.ciudad+' '+venta.sucursal.estado+', '+venta.sucursal.pais)



	#copia
	p.setFont("Helvetica-Bold",7)
	p.drawString(55,690 - pos_copia,"Empresa:")
	p.setFont("Helvetica",7)
	p.drawString(55,680- pos_copia,"   " + Empresa.objects.get(id = 1).nombre_empresa)
	p.setFont("Helvetica",7)
	p.drawString(55,670- pos_copia,"      L-V 9 AM. a 6 PM.  S 10:00 AM a 4:00 PM.")

	p.setFont("Helvetica-Bold",7)
	p.drawString(55,650 - pos_copia,"RFC:")
	p.setFont("Helvetica",7)
	p.drawString(75,650 - pos_copia,Empresa.objects.get(id = 1).rfc)
	p.setFont("Helvetica-Bold",7)
	p.drawString(170,650 - pos_copia,"Telefono:")
	p.setFont("Helvetica",7)
	p.drawString(210,650 - pos_copia,venta.sucursal.telefono)

	p.setFont("Helvetica-Bold",7)
	p.drawString(55,640 - pos_copia,"Dirección:")
	p.setFont("Helvetica",7)
	p.drawString(100,640 - pos_copia,venta.sucursal.calle+' No. Int. '+str(venta.sucursal.numero_interior)+' No. ext. '+str(venta.sucursal.numero_exterior))
	p.setFont("Helvetica",7)
	p.drawString(55,630 - pos_copia,' CP ' + str(venta.sucursal.codigo_postal) + ' ' + venta.sucursal.colonia + ', '+venta.sucursal.ciudad+' '+venta.sucursal.estado+', '+venta.sucursal.pais)





	#cuadro 2] Informacion general de la boleta
	p.line(300,730,300,615)	
	p.line(300,730,550,730)
	p.line(550,730,550,615)	
	p.line(300,615,550,615)

	#copia
	#cuadro 2] Informacion general de la boleta
	p.line(300,730 - pos_copia,300,615 - pos_copia)	
	p.line(300,730 - pos_copia,550,730 - pos_copia)
	p.line(550,730 - pos_copia,550,615 - pos_copia)	
	p.line(300,615 - pos_copia,550,615 - pos_copia)
	p.setFont("Helvetica-Bold",10)


	p.drawString(305,720,"Venta piso")
	#copia
	p.drawString(305,720 - pos_copia,"Venta piso")

	#p.drawString(455,790,"Pag: "+str(cont_pag)+' de '+str(no_paginas))
	p.setFont("Helvetica-Bold",15)
	p.drawString(305,700,"Folio venta piso:")
	p.setFont("Helvetica-Bold",15)
	p.drawString(455,700,fn_str_clave(venta.folio))



	p.setFont("Helvetica-Bold",10)
	p.drawString(305,680,"Fecha venta:")
	p.setFont("Helvetica",10)
	p.drawString(400,680,txt_hoy)


	p.setFont("Helvetica-Bold",10)
	p.drawString(305,665,"Cajero:")

	p.setFont("Helvetica",10)
	
	p.drawString(400,665,venta.usuario.username)

	#copia
	p.setFont("Helvetica-Bold",15)
	p.drawString(305,700 - pos_copia,"Folio venta piso:")
	p.setFont("Helvetica-Bold",15)
	p.drawString(455,700 - pos_copia,fn_str_clave(venta.folio))



	p.setFont("Helvetica-Bold",10)
	p.drawString(305,680 - pos_copia,"Fecha venta:")
	p.setFont("Helvetica",10)
	p.drawString(400,680 - pos_copia,txt_hoy)


	p.setFont("Helvetica-Bold",10)
	p.drawString(305,665 - pos_copia,"Cajero:")

	p.setFont("Helvetica",10)
	
	p.drawString(400,665 - pos_copia,venta.usuario.username)

	#cuadro 3] Informacion de Cliente
	p.line(50,610,50,545)	
	p.line(550,610,550,545)	
	p.line(50,610,550,610)	
	p.line(50,545,550,545)	

	p.setFont("Helvetica-Bold",7)
	p.drawString(55,595,"Cliente:")
	p.setFont("Helvetica",7)
	p.drawString(105,595,venta.nombre_cliente)


	p.setFont("Helvetica-Bold",7)
	p.drawString(55,580,"Teléfono:")
	p.setFont("Helvetica",7)
	p.drawString(105,580,venta.telefono)




	#copia
	#cuadro 3] Informacion de Cliente
	p.line(50,610 - pos_copia,50,545 - pos_copia)	
	p.line(550,610 - pos_copia,550,545 - pos_copia)	
	p.line(50,610 - pos_copia,550,610 - pos_copia)	
	p.line(50,545 - pos_copia,550,545 - pos_copia)	

	p.setFont("Helvetica-Bold",7)
	p.drawString(55,595 - pos_copia,"Cliente:")
	p.setFont("Helvetica",7)
	p.drawString(105,595 - pos_copia,venta.nombre_cliente)


	p.setFont("Helvetica-Bold",7)
	p.drawString(55,580 - pos_copia,"Teléfono:")
	p.setFont("Helvetica",7)
	p.drawString(105,580 - pos_copia,venta.telefono)



	#cuadro 4] Productos
	p.line(50,540,50,480)	
	p.line(550,540,550,480)	
	p.line(50,540,550,540)	
	p.line(50,480,550,480)

	p.setFont("Helvetica",7)
	p.drawString(55,530,"Artículos")
	p.drawString(500,530,"Precio")
	p.line(50,525,550,525)


	#cuadro 4] Productos
	#copia
	p.line(50,540- pos_copia,50,480- pos_copia)	
	p.line(550,540- pos_copia,550,480- pos_copia)	
	p.line(50,540- pos_copia,550,540- pos_copia)	
	p.line(50,480- pos_copia,550,480- pos_copia)

	p.setFont("Helvetica",7)
	p.drawString(55,530- pos_copia,"Artículos")
	p.drawString(500,530- pos_copia,"Precio")
	p.line(50,525- pos_copia,550,525- pos_copia)

	dv = Det_Venta_Piso.objects.filter(venta = venta)

	r=15
	ract = 525

	for d in dv:

		ract = ract-r	
		#articulos varios
		if d.boleta.tipo_producto.id == 3:
			db = Det_Boleto_Empeno.objects.get(boleta_empeno = d.boleta)
				
			p.drawString(55,ract+2,"fb:"+str(d.boleta.folio)+"; "+db.descripcion)

		#articulos Oro
		if d.boleta.tipo_producto.id == 1:		
			
			p.drawString(55,ract+2,"fb:"+str(d.boleta.folio)+"; Joyería Oro")

		#articulos Plata
		if d.boleta.tipo_producto.id == 2:		
			
			p.drawString(55,ract+2,"fb:"+str(d.boleta.folio)+"; Joyería Plata")

		precio_venta = "{:0,.2f}".format(d.boleta.fn_calcula_precio_venta())

		p.drawString(500,ract+2,"$"+precio_venta)
		#copia
		
		#articulos varios
		if d.boleta.tipo_producto.id == 3:
			db = Det_Boleto_Empeno.objects.get(boleta_empeno = d.boleta)
				
			p.drawString(55,ract+2- pos_copia,"fb:"+str(d.boleta.folio)+"; "+db.descripcion)

		#articulos Oro
		if d.boleta.tipo_producto.id == 1:		
			
			p.drawString(55,ract+2- pos_copia,"fb:"+str(d.boleta.folio)+"; Joyería Oro")

		#articulos Plata
		if d.boleta.tipo_producto.id == 2:		
			
			p.drawString(55,ract+2- pos_copia,"fb:"+str(d.boleta.folio)+"; Joyería Plata")

		precio_venta = "{:0,.2f}".format(d.boleta.fn_calcula_precio_venta())

		p.drawString(500,ract+2- pos_copia,"$"+precio_venta)
	
	
	if dv.count() == 1:
		ract = ract-r
		ract = ract-r
		ract = ract-r	

	if dv.count() == 2:
		ract = ract-r
		ract = ract-r

	if dv.count() == 3:
		ract = ract-r
	
	importe_venta = "{:0,.2f}".format(venta.importe_venta)

	p.setFont("Helvetica-Bold",10)
	p.drawString(450,ract+2,"Total:")
	p.drawString(500,ract+2,"$"+importe_venta)

	#copia
	p.setFont("Helvetica-Bold",10)
	p.drawString(450,ract+2- pos_copia,"Total:")
	p.drawString(500,ract+2- pos_copia,"$"+importe_venta)

	r=15
	ract = 525
	ract = ract-r
	p.line(50,ract,550,ract)
	ract = ract-r
	p.line(50,ract,550,ract)
	ract = ract-r
	p.line(50,ract,550,ract)

	ract = ract-r
	ract = ract-r	
	ract = ract-r

	p.line(100,ract,200,ract)
	p.line(400,ract,500,ract)

	ract = ract-10
	p.setFont("Helvetica-Bold",7)
	p.drawString(90,ract+2,'Cliente: ' + venta.nombre_cliente)
	p.drawString(400,ract+2,'Cajero: ' + venta.usuario.username)
	
	
	
	#copia

	


	r=15
	ract = 525
	ract = ract-r
	p.line(50,ract- pos_copia,550,ract- pos_copia)
	ract = ract-r
	p.line(50,ract- pos_copia,550,ract- pos_copia)
	ract = ract-r
	p.line(50,ract- pos_copia,550,ract- pos_copia)

	ract = ract-r
	ract = ract-r	
	ract = ract-r

	p.line(100,ract- pos_copia,200,ract- pos_copia)
	p.line(400,ract- pos_copia,500,ract- pos_copia)

	ract = ract-10
	p.setFont("Helvetica-Bold",7)
	p.drawString(90,ract+2- pos_copia,'Cliente: ' + venta.nombre_cliente)
	p.drawString(400,ract+2- pos_copia,'Cajero: ' + venta.usuario.username)
	
	

	linea_corte=50

	pinta=0
	while linea_corte<600:
		if pinta==0:
			p.line(linea_corte,400,linea_corte-20,400)
			pinta=1
		else:
			
			pinta=0

		linea_corte=linea_corte+20

	p.save()
	pdf=buffer.getvalue()
	buffer.close()
	response.write(pdf)
	return response




def rep_boleta_empeno(obj_reporte,leyenda,request):
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
			#p.drawString(300,520, "Sucursal: " + sucursal)
			p.drawString(300,520, "Reporte de boletas  " + leyenda)

			row_act = 480
			row_size = 20
			p.line(55,row_act,545,row_act)
			row_act = row_act - row_size
			p.drawString(60,row_act+5,"Folio")
			p.drawString(100,row_act+5,"Usuario")
			p.drawString(160,row_act+5,"Avaluo")
			p.drawString(230,row_act+5,"Mutuo")
			p.drawString(290,row_act+5,"Refrendo")
			p.drawString(360,row_act+5,"Tipo producto")			
			p.drawString(450,row_act+5,"plazo")
			p.drawString(500,row_act+5,"Fecha emi.")
			p.drawString(580,row_act+5,"Fecha venc.")
			p.drawString(660,row_act+5,"Estatus")

			p.line(55,row_act,55,row_act+20)#folio
			p.line(95,row_act,95,row_act+20)#usuario
			p.line(155,row_act,155,row_act+20)#avaluo
			p.line(225,row_act,225,row_act+20)#mutuo

			p.line(285,row_act,285,row_act+20)#refrendo

			p.line(355,row_act,355,row_act+20)#tipo producto

			p.line(445,row_act,445,row_act+20)#plazo
			p.line(495,row_act,495,row_act+20)#fecha emision
			p.line(575,row_act,575,row_act+20)#fecha vencimiento
			p.line(655,row_act,655,row_act+20)#estatus
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

		p.line(445,row_act,445,row_act+20)#diferencia

		p.line(495,row_act,495,row_act+20)
		p.line(575,row_act,575,row_act+20)
		p.line(655,row_act,655,row_act+20)
		p.line(725,row_act,725,row_act+20)

		p.line(55,row_act,725,row_act)

		p.setFont("Helvetica",7)
		p.drawString(60,row_act+5,fn_str_clave(o.folio))				#folio

		p.drawString(100,row_act+5,o.usuario.username)				#usuario
		avaluo = "{:0,.2f}".format(o.avaluo)
		p.drawString(160,row_act+5,"$"+avaluo)				#avaluo

		mutuo = "{:0,.2f}".format(o.mutuo)
		p.drawString(230,row_act+5,"$"+mutuo)				#mutuo

		refrendo = "{:0,.2f}".format(o.refrendo)
		p.drawString(290,row_act+5,"$"+refrendo)				#refrendo

		p.drawString(360,row_act+5,o.tipo_producto.tipo_producto)				#tipo producto

		p.drawString(450,row_act+5,o.plazo.plazo)				#plazo

		p.drawString(500,row_act+5,datetime.strftime(o.fecha,'%Y-%m-%d'))				#fecha emision
		p.drawString(580,row_act+5,datetime.strftime(o.fecha_vencimiento,'%Y-%m-%d'))				#fecha vencimiento
		p.drawString(660,row_act+5,o.estatus.estatus)				#estatus

		row_act = row_act - row_size
		if cont == 20:
			p.showPage()

	p.setFont("Helvetica-Bold",7)
	p.drawString(60,row_act+5,"Total")				#folio

	avaluo = "{:0,.2f}".format(obj_reporte.aggregate(Sum("avaluo"))["avaluo__sum"])
	p.drawString(160,row_act+5,"$"+avaluo)				#avaluo

	mutuo = "{:0,.2f}".format(obj_reporte.aggregate(Sum("mutuo"))["mutuo__sum"])
	p.drawString(230,row_act+5,"$"+mutuo)				#mutuo

	
	refrendo = "{:0,.2f}".format(obj_reporte.aggregate(Sum("refrendo"))["refrendo__sum"])
	p.drawString(290,row_act+5,"$"+refrendo)				#refrendo

	p.drawString(360,row_act+5,"Numero de boletas: " + str(obj_reporte.count()))				#refrendo


	p.line(55,row_act,55,row_act+20)
	
	p.line(155,row_act,155,row_act+20)
	p.line(225,row_act,225,row_act+20)#usuario cierre

	p.line(285,row_act,285,row_act+20)#teorico cierre

	p.line(355,row_act,355,row_act+20)#real cierre


	p.line(725,row_act,725,row_act+20)

	p.line(55,row_act,725,row_act)
	p.save()
	pdf=buffer.getvalue()
	buffer.close()
	response.write(pdf)
	return response

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

	p.drawString(310,row_act+5,"10 Centavos")
	p.drawString(500,row_act+5,str(caja[1]["centavos_10"]))
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
	p.drawString(310,row_act+5,"50 Centavos")
	p.drawString(500,row_act+5,str(caja[1]["centavos_50"]))
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
	p.drawString(60,row_act+5,"Comisiónes PG")
	p.drawString(150,row_act+5,str(caja[0]["cont_com_pg"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_comisiones_pg"]))
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
	p.drawString(60,row_act+5,"Pago capital")
	p.drawString(150,row_act+5,str(caja[0]["cont_pc"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_pago_capital"]))
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
	p.drawString(60,row_act+5,"Desempeño")
	p.drawString(150,row_act+5,str(caja[0]["cont_desemp"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_importe_desemp"]))
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
	p.drawString(60,row_act+5,"Reimp. Boleta")
	p.drawString(150,row_act+5,str(caja[0]["cont_rebol"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_importe_rebol"]))
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
	p.drawString(60,row_act+5,"Ventas")
	p.drawString(150,row_act+5,str(caja[0]["cont_ventas"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_importe_ventas"]))
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
	p.drawString(60,row_act+5,"Abono apartado")
	p.drawString(150,row_act+5,str(caja[0]["cont_ab_apartado"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_importe_apartado"]))
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
	p.setFont("Helvetica-Bold",10)
	#########
	p.drawString(60,row_act+5,"Salidas teórico")	
	p.setFont("Helvetica",10)
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
	p.drawString(60,row_act+5,"Retiro de caja")
	p.drawString(150,row_act+5,str(caja[0]["cont_retiros"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_retiros"]))
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
	#########
	p.drawString(60,row_act+5,"Empeños")
	p.drawString(150,row_act+5,str(caja[0]["cont_empenos"]))
	otros_ingresos = "{:0,.2f}".format(float(caja[0]["f_empenos"]))
	p.drawString(210,row_act+5,"$" + otros_ingresos)
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
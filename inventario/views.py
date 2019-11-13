from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from .models import Productos,Atributos,Tallas,Img_Producto,Estatus,Productos_Relacionados,Municipio,Estado,Pais
from .models import Rel_Producto_Categoria,Categorias,Proveedor
from django.http import QueryDict
from django.db.models import Sum
from .forms import Productos_Form,Proveedores_Form,Busqueda_Producto_Form,Busca_Proveedores_Form
from .forms import Categorias_Form,Busca_X_Clave_Prod_Prov_Form
import decimal
from django.forms.models import inlineformset_factory
from django.template import RequestContext as ctx
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate

#formulario de busqueda de producto
def busca_producto(request):	
	if not request.user.is_authenticated:	
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if request.method=="POST":		
		if request.POST.get("id_proveedor")=='':
			proveedor=0
		else:
			proveedor=int(request.POST.get("id_proveedor"))
			
		if request.POST.get("id_estatus")=='':
			estatus=0
		else:
			estatus=int(request.POST.get("id_estatus"))
			
		if proveedor==0 and estatus==0:
			producto=Productos.objects.all()
		if proveedor>0 and estatus==0:
			producto=Productos.objects.filter(id_proveedor=proveedor)
		if estatus>0 and proveedor==0:
			producto=Productos.objects.filter(id_estatus=estatus)
		if proveedor>0 and estatus>0:
			producto=Productos.objects.filter(id_proveedor=proveedor,id_estatus=estatus)						
		form=Busqueda_Producto_Form(request.POST)			
	else:
		producto=Productos.objects.all()
		form=Busqueda_Producto_Form()	
	return render(request,'inventario/busca_producto.html',locals())

def busca_proveedor(request):
	if not request.user.is_authenticated:	
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if request.method=="POST":
		proveedor=request.POST.get("nombre_proveedor")
		proveedor=Proveedor.objects.filter(proveedor__icontains=proveedor)
		form=Busca_Proveedores_Form(request.POST)
	else:
		proveedor=Proveedor.objects.all()
		form=Busca_Proveedores_Form()
	return render(request,'inventario/busca_proveedor.html',locals())

def busca_categoria(request):
	categoria=Categorias.objects.all()
	return render(request,'inventario/busca_categoria.html',locals())
	
#formulario alta de proveedores
def proveedores_edicion_registro(request,id_proveedor=None):
	if not request.user.is_authenticated:	
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if id_proveedor:
		proveedor=Proveedor.objects.get(id=id_proveedor)
	else:
		proveedor=Proveedor()	
		
	if request.method=="POST":
		form=Proveedores_Form(request.POST,instance=proveedor)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('inventario:busca_proveedor'))
	else:
		form=Proveedores_Form(instance=proveedor)
	return render(request,'inventario/proveedor.html',locals())	

def categoria_edicion_registro(request,id_categoria=None):
	if not request.user.is_authenticated:	
		return HttpResponseRedirect(reverse('seguridad:login'))
	if id_categoria:
		categoria=Categorias.objects.get(id=id_categoria)
	else:
		categoria=Categorias()
	if request.method=="POST":
		form=Categorias_Form(request.POST,instance=categoria)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('inventario:busca_categoria'))
	else:
		form=Categorias_Form(instance=categoria)
	return render(request,'inventario/categoria.html',locals())
	
#formulario de alta de producto
def registro_edicion_producto(request,id_producto=None):
	if not request.user.is_authenticated:	
		return HttpResponseRedirect(reverse('seguridad:login'))

	if id_producto:
		producto=Productos.objects.get(id=id_producto)
	else:
		producto=Productos()			
		
	#creamos los formsets	
	Atributo_Formset=inlineformset_factory(Productos,Atributos,fields=["atributo","valor_atributo",],extra=1,can_delete=True)		
	Talla_Formset=inlineformset_factory(Productos,Tallas,fields=["talla",],extra=1,max_num=10,can_delete=True)
	#imagenes_formset=inlineformset_factory(Productos,Img_Producto,fields=["nom_img","orden",],extra=2,can_delete=False)
	Productos_Relacionados_Formset=inlineformset_factory(Productos,Productos_Relacionados,fields=["id_producto_relacionado",],fk_name="id_producto",extra=1,can_delete=True)	
	Rel_Producto_Categoria_Formset=inlineformset_factory(Productos,Rel_Producto_Categoria,fields=["id_producto","id_categoria",],fk_name="id_producto",extra=1,can_delete=True)
	Img_Producto_Formset=inlineformset_factory(Productos,Img_Producto,fields=["nom_img",'orden',],fk_name="id_producto",extra=1,can_delete=True)
	if request.method=="POST":	
		form=Productos_Form(request.POST,instance=producto)
		atributo_formset=Atributo_Formset(request.POST,instance=producto)
		talla_formset=Talla_Formset(request.POST,instance=producto)
		productos_relacionados_formset=Productos_Relacionados_Formset(request.POST,instance=producto)		
		rel_producto_categoria_formset=Rel_Producto_Categoria_Formset(request.POST,instance=producto)
		img_producto_formset=Img_Producto_Formset(request.POST,instance=producto)
		if form.is_valid() and atributo_formset.is_valid() and talla_formset.is_valid() and productos_relacionados_formset.is_valid() and rel_producto_categoria_formset.is_valid() and img_producto_formset.is_valid():
			form.save()
			atributo_formset.save()
			talla_formset.save()
			productos_relacionados_formset.save()
			rel_producto_categoria_formset.save()			
			img_producto_formset.save()
			return HttpResponseRedirect(reverse('inventario:busca_producto'))
	else:	
		form=Productos_Form(instance=producto)
		atributo_formset=Atributo_Formset(instance=producto)
		talla_formset=Talla_Formset(instance=producto)
		#imagenes_formset=imagenes_formset(instance=producto)
		productos_relacionados_formset=Productos_Relacionados_Formset(instance=producto)
		rel_producto_categoria_formset=Rel_Producto_Categoria_Formset(instance=producto)			
		img_producto_formset=Img_Producto_Formset(instance=producto)
	return render(request,'inventario/producto.html',locals())
	
def edicion_existencias(request,id_producto=None):		
	if not request.user.is_authenticated:	
		return HttpResponseRedirect(reverse('seguridad:login'))

	if id_producto:
		producto=Productos.objects.get(id=id_producto)
	else:
		producto=Productos()			
	Talla_Formset=inlineformset_factory(Productos,Tallas,fields=["talla","entrada","salida"],extra=0,can_delete=True)
	if request.method=="POST":
		form=Productos_Form(request.POST,instance=producto)
		tallas_formset=Talla_Formset(request.POST,instance=producto)
		if tallas_formset.is_valid():
			tallas_formset.save()
			return HttpResponseRedirect(reverse('inventario:busca_producto'))
	else:
		form=Productos_Form(instance=producto)
		tallas_formset=Talla_Formset(instance=producto)
	return render(request,'inventario/entrada_producto.html',locals())
	
#esta api se usara sobre todo en la consulta del producto,
#parametro:
#	id: REcibe el id del producto que desea consultar.
#	return: regresa toda la informacion relacionada con el producto que desea consultar.
@api_view(['GET'])
def api_consulta_producto(request):	
	producto=[]
	try:
		atributos=[]
		tallas=[]
		img_prod=[]
		p_r=[]
		#parametros
		
		#print(request.GET.get("id_producto"))
		
		id_producto=int_clave(request.GET.get("id_producto"))
		#..		
		
		est=Estatus.objects.get(id=1)
		
		#obtenemos el producto
		prod=Productos.objects.get(id=id_producto,id_estatus=est)
		
		#obtenemos los atributos del producto
		att=Atributos.objects.filter(id_producto=prod)
		
		#validamos que contenga atributos
		if att.exists():
			for a in att:
				atributos.append({'atributo':a.atributo,'valor_atributo':a.valor_atributo})
		
		#obtenemos las tallas del producto
		ta=Tallas.objects.filter(id_producto=prod)		
		
		#validamos que tenga tallas registradas
		if ta.exists():
			for t in ta:
				tallas.append({'id_talla':t.id,'talla':t.talla})
		
		#obtenemos las imagenes del producto
		img=Img_Producto.objects.filter(id_producto=prod).order_by('id')
		
		#obtenemos los productos relacionados
		prod_r=Productos_Relacionados.objects.filter(id_producto=prod)
		
		if prod_r.exists():
			for p in prod_r:
				#obtenemos la imagen relacionada que sea orden 1
				#la imagen con orden  1 deberia ser la img principal del producto
				try:
					img_r=Img_Producto.objects.get(id_producto=p.id_producto_relacionado,orden=1)				
					p_r.append({'id_producto_relacionado':p.id_producto_relacionado.id,'nombre_producto':p.id_producto_relacionado.nombre,'img_producto_rel':img_r.nom_img,'orden':img_r.orden,'precio':p.id_producto_relacionado.precio})
				except Exception as e:
					print("el producto no tiene productos relacionados con el orden valor=1")
					print(e)
					img_r=[]
			
		#validamos que tenga imagenes
		if img.exists():
			for i in img:
				img_prod.append({'img_producto':i.nom_img,'orden':i.orden})
		
		producto.append({'precio':prod.precio,'id_producto':prod.id,'nom_producto':prod.nombre,'desc_producto':prod.desc_producto,'atributos':atributos,'tallas':tallas,'img_prod':img_prod,'descuento':prod.descuento,'prod_relacionado':p_r})	
	except Exception as e:
		print(e)	
	return Response(producto)
		
#esta api busca los productos dependiendo de los parametros que se indiquen
#parametros:
#	tipo_busqueda: 
#					1=indica que se buscara por la categoria (id_categoria)	
#					2= indica que se recibira una palabra y se buscaran los productos que contengan esa palabra en sus atributos			
@api_view(['GET'])
def api_busqueda_productos(request):
	productos=[]
	muestra_descuento=0
	if request.method=="GET":						
		tipo_busqueda=request.GET.get("tipo_busqueda")
		est=Estatus.objects.get(id=1)#obtenemos el estatus "activo" del catalogo				
		if tipo_busqueda=="1":#busqueda por categoria.
			id=request.GET.get("param1")		
			try:
				id_categoria=Categorias.objects.get(id=id)			
			except Exception as e:
				print (e)#si la categoria no existe, pues no encontramos productos.			
				return Response(productos)	
			p_e=Rel_Producto_Categoria.objects.filter(id_categoria=id_categoria)
			if p_e.exists():
				for p in p_e:
					try:
						tallas_entrada=Tallas.objects.filter(id_producto=p.id_producto).aggregate(Sum('entrada'))
						tallas_salida=Tallas.objects.filter(id_producto=p.id_producto).aggregate(Sum('salida'))
						cont=int(tallas_entrada["entrada__sum"])-(tallas_salida["salida__sum"])
					except:
						cont=0
					
					if cont>0:
						print("entro")
						if p.id_producto.id_estatus==est:#validamos que el producto este activo
							#imagen=Img_Producto.objects.get(id_producto=p.id_producto,orden=1)
							#precio_desc=decimal.Decimal(p.id_producto.precio)*decimal.Decimal((decimal.Decimal(p.id_producto.descuento)/100.00))
							precio_desc=p.id_producto.precio-(p.id_producto.precio*(decimal.Decimal(p.id_producto.descuento/100.00)))
							if p.id_producto.descuento>0:
								muestra_descuento=1
							else:
								muestra_descuento=0
							productos.append({"descuento":p.id_producto.descuento,"precio_antes":p.id_producto.precio,"id":p.id_producto.id,'str_id':str_clave(p.id_producto.id),"nombre":p.id_producto.nombre,"precio":precio_desc,'muestra_descuento':muestra_descuento})				
		if tipo_busqueda=="2":#busqueda por palabra		
			text_busqueda=request.GET.get("param1")										
			print(text_busqueda)
			prod=Productos.objects.filter(desc_producto__icontains=str(text_busqueda))							
			#p_e=Rel_Producto_Categoria.objects.filter(id_producto__in=prod)
			
			if prod.exists():
				for p in prod:
					try:
						tallas_entrada=Tallas.objects.filter(id_producto=p).aggregate(Sum('entrada'))
						tallas_salida=Tallas.objects.filter(id_producto=p).aggregate(Sum('salida'))
						cont=int(tallas_entrada["entrada__sum"])-(tallas_salida["salida__sum"])
					except:
						cont=0
					
					if cont>0:						
						if p.id_estatus==est:#validamos que el producto este activo
							#imagen=Img_Producto.objects.get(id_producto=p.id_producto,orden=1)
							#precio_desc=decimal.Decimal(p.id_producto.precio)*decimal.Decimal((decimal.Decimal(p.id_producto.descuento)/100.00))
							precio_desc=p.precio-(p.precio*(decimal.Decimal(p.descuento/100.00)))
							if p.descuento>0:
								muestra_descuento=1
							else:
								muestra_descuento=0
							productos.append({"descuento":p.descuento,"precio_antes":p.precio,"id":p.id,'str_id':str_clave(p.id),"nombre":p.nombre,"precio":precio_desc,'muestra_descuento':muestra_descuento})				
	return Response(productos)	
	
#api para consultar el catalogo de municipios
@api_view(['GET'])
def api_get_municipios(request):
	cat_municipio=[]
	try:
		mun=Municipio.objects.all()
		for m in mun:
			cat_municipio.append({'id_municipio':m.id,'municipio':m.municipio})
	except Exception as e:	
		print(e)
	return Response(cat_municipio)
			
def str_clave(id):
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

def int_clave(id):
	return int(id)

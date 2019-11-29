from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate
from .forms import Blog_Form,Busqueda_Blog_Form
from .models import Blog,Productos_Relacionados,Rel_Blog_Blog,ContenidoBlog
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.forms.models import inlineformset_factory
from inventario.models import Img_Producto

def alta_edicion_blog(request,id_blog=None):
	if not request.user.is_authenticated:	
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if id_blog:
		blog=Blog.objects.get(id=id_blog)
	else:
		blog=Blog()
	
	Productos_Relacionados_Formset=inlineformset_factory(Blog,Productos_Relacionados,fields=["id_producto_relacionado",],fk_name="id_blog",extra=1,can_delete=True)
	Contenido_Blog_Formset=inlineformset_factory(Blog,ContenidoBlog,fields=["contenido_blog"],fk_name="id_blog",extra=1,can_delete=True)
	Blog_Relacionados=inlineformset_factory(Blog,Rel_Blog_Blog,fields=["id_blog","id_blog_relacionado",],fk_name="id_blog",extra=1,can_delete=True)
	
	if request.method=="POST":
		form=Blog_Form(request.POST,instance=blog)
		productos_relacionados_formset=Productos_Relacionados_Formset(request.POST,instance=blog)
		blog_relacionados=Blog_Relacionados(request.POST,instance=blog)
		contenido_blog_formset=Contenido_Blog_Formset(request.POST,instance=blog)
		if form.is_valid() and productos_relacionados_formset.is_valid() and blog_relacionados.is_valid() and contenido_blog_formset.is_valid():
			form.save()			
			productos_relacionados_formset.save()
			blog_relacionados.save()
			contenido_blog_formset.save()
			return HttpResponseRedirect(reverse('blog:busqueda_blog'))
	else:
		form=Blog_Form(instance=blog)
		productos_relacionados_formset=Productos_Relacionados_Formset(instance=blog)
		blog_relacionados=Blog_Relacionados(instance=blog)
		contenido_blog_formset=Contenido_Blog_Formset(instance=blog)
	return render(request,'blog/alta_blog.html',locals())
	

def busqueda_blog(request):
	
	if request.method=="POST":
		fecha_i=request.POST.get("fecha_inicial")
		fecha_f=request.POST.get("fecha_final")
		
		
		if request.POST.get("id_estatus"):		
			id_estatus=int(request.POST.get("id_estatus"))
		else:			
			id_estatus=0
		
		if fecha_i=="" and fecha_f=="" and id_estatus==0:						
			blog=Blog.objects.all()
			
		if fecha_i!="" and fecha_i!="":
			if id_estatus>0:
				blog=Blog.objects.filter(fecha__range=(fecha_i,fecha_f),id_estatus=id_estatus)		
			else:
				blog=Blog.objects.filter(fecha__range=(fecha_i,fecha_f))		
		
		if id_estatus>0:
			if fecha_i!="" and fecha_i!="":
				blog=Blog.objects.filter(fecha__range=(fecha_i,fecha_f),id_estatus=id_estatus)		
			else:
				blog=Blog.objects.filter(id_estatus=id_estatus)		
		form=Busqueda_Blog_Form(request.POST)
	else:
		form=Busqueda_Blog_Form()
		blog=Blog.objects.all()
		print(blog)
	return render(request,'blog/busca_blog.html',locals())

@api_view(["GET"])
def api_consulta_blogs(request):
	blog=[]
	try:
		#obtenemos los blogs activos
		b=Blog.objects.filter(id_estatus=1)
		for x in b:
			blog.append({"id_blog":x.id,"nombre_blog":x.nombre_blog,"imagen_blog":x.imagen_blog})
	except Exception as e:
		print(e)
	return Response(blog)

#recibimos com parametro id_blogS
@api_view(["GET"])
def api_consulta_detalle_blog(request):
	detalle_blog=[]
	contenido_blog=[]
	b_r=[]
	p_r=[]
	primer_parrafo=""
	try:
		b=Blog.objects.get(id=int(request.GET.get("id_blog")))
		primer_parrafo=ContenidoBlog.objects.filter(id_blog=b)[:1]
		c_b=ContenidoBlog.objects.filter(id_blog=b)
		cont=0
		for x in c_b:
			if cont==0:
				primer_parrafo=x.contenido_blog
				cont=1
			else:
				contenido_blog.append({"parrafo":x.contenido_blog})
				cont=1
		#********************************************************************************************
		#obtenemos los productos relacionados
		prod_r=Productos_Relacionados.objects.filter(id_blog=b)
		
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
					
		#********************************************************************************************
		#obtenemos los blogs relacionados
		blog_r=Rel_Blog_Blog.objects.filter(id_blog=b)
		if blog_r.exists():
			for br in blog_r:
				b_r.append({"id_blog":br.id_blog_relacionado.id,"nombre_blog":br.id_blog_relacionado.nombre_blog,"imagen_blog":br.id_blog_relacionado.imagen_blog})
		detalle_blog.append({"autor":b.autor,"puesto_autor":b.puesto_autor,"id_blog":b.id,"nombre_blog":b.nombre_blog,"imagen_blog":b.imagen_blog,"fecha":b.fecha,"contenido":contenido_blog,"primer_parrafo":primer_parrafo,'prod_relacionado':p_r,'blog_relacionados':b_r})		
	except Exception as e:
		print(e)
	return Response(detalle_blog)
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate
from .forms import Blog_Form,Busqueda_Blog_Form
from .models import Blog,Productos_Relacionados,Rel_Blog_Blog
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.forms.models import inlineformset_factory

def alta_edicion_blog(request,id_blog=None):
	if not request.user.is_authenticated:	
		return HttpResponseRedirect(reverse('seguridad:login'))
		
	if id_blog:
		blog=Blog.objects.get(id=id_blog)
	else:
		blog=Blog()
	
	Productos_Relacionados_Formset=inlineformset_factory(Blog,Productos_Relacionados,fields=["id_producto_relacionado",],fk_name="id_blog",extra=1,can_delete=True)
	Blog_Relacionados=inlineformset_factory(Blog,Rel_Blog_Blog,fields=["id_blog","id_blog_relacionado",],fk_name="id_blog",extra=1,can_delete=True)
	
	if request.method=="POST":
		form=Blog_Form(request.POST,instance=blog)
		productos_relacionados_formset=Productos_Relacionados_Formset(request.POST,instance=blog)
		blog_relacionados=Blog_Relacionados(request.POST,instance=blog)
		if form.is_valid() and productos_relacionados_formset.is_valid() and blog_relacionados.is_valid():
			form.save()			
			productos_relacionados_formset.save()
			blog_relacionados.save()
			return HttpResponseRedirect(reverse('blog:busqueda_blog'))
	else:
		form=Blog_Form(instance=blog)
		productos_relacionados_formset=Productos_Relacionados_Formset(instance=blog)
		blog_relacionados=Blog_Relacionados(instance=blog)
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
		blog=Blog.objects.all()[:10]
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
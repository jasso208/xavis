from django.conf.urls import include,url

from blog import views

app_name="blog"
urlpatterns=[
	#formularios
	url(r'^new/$',views.alta_edicion_blog,name="alta_blog"),
	url(r'^busqueda_blog/$',views.busqueda_blog,name="busqueda_blog"),
	url(r'^edita_blog/(?P<id_blog>\d+)/$',views.alta_edicion_blog,name="edita_blog"),
	
	
	#apis
	url(r'^consulta_blogs/$',views.api_consulta_blogs,name="consulta_blogs"),
	
	
	#apis
	#url(r'^carrito_compras/$',api_consulta_carrito_compras),	
	
]


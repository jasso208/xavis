from django.conf.urls import include, url
from .views import api_consulta_producto,api_get_municipios
from .views import api_busqueda_productos
from inventario import views

app_name="inventario"

urlpatterns=[
	#formularios
	url(r'^busca_producto/$',views.busca_producto,name="busca_producto"),		
	url(r'^consulta_stock/$',views.consulta_stock,name="consulta_stock"),	

	url(r'^busca_proveedor/$',views.busca_proveedor,name="busca_proveedor"),
	url(r'^busca_categoria/$',views.busca_categoria,name="busca_categoria"),	
	url(r'^productos/new/$',views.registro_edicion_producto,name="producto"),	
	url(r'^existencias/(?P<id_producto>\d+)/$',views.edicion_existencias,name="existencias"),
	url(r'^proveedor/new/$',views.proveedores_edicion_registro,name="proveedor"),
	url(r'^categoria/new/$',views.categoria_edicion_registro,name="categoria"),
	url(r'^productos_edita/(?P<id_producto>\d+)/$',views.registro_edicion_producto,name="edicion_producto"),
	url(r'^proveedor_edita/(?P<id_proveedor>\d+)/$',views.proveedores_edicion_registro,name="edicion_proveedor"),
	url(r'^categoria_edita/(?P<id_categoria>\d+)/$',views.categoria_edicion_registro,name="edicion_categoria"),

	
	#urls de apis
	url(r'^detalle_producto/$',api_consulta_producto),		
	url(r'^busca_productos/$',api_busqueda_productos),	
	url(r'^busca_prod_x_bloque/$',views.api_busca_prod_x_bloque),		
	
]

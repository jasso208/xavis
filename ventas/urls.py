from django.conf.urls import include,url
from .views import api_cont_productos_carrito,api_crea_venta,api_direccion_envio,api_consulta_carrito_compras,api_elimina_carrito_compras

from ventas import views

app_name="ventas"
urlpatterns=[
	#formularios
	url(r'^busca_ventas/$',views.busca_ventas,name="busca_ventas"),
	url(r'^detalle_venta/(?P<id_venta>\d+)/$',views.detalle_venta_form,name="detalle_venta"),
	
	#apis
	url(r'^carrito_compras/$',api_consulta_carrito_compras),	
	url(r'^elimina_prod_carrito/$',api_elimina_carrito_compras),		
	url(r'^direccion_envio/$',api_direccion_envio),	
	
	url(r'^cont_prod_carrito/$',api_cont_productos_carrito),		
	url(r'^guarda_venta/$',api_crea_venta),		
]


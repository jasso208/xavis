from django.conf.urls import include, url
from .views import api_consulta_producto,api_consulta_carrito_compras,api_elimina_carrito_compras,api_get_municipios,api_direccion_envio
from .views import api_busqueda_productos,api_cont_productos_carrito,api_crea_venta
urlpatterns=[
	url(r'^detalle_producto/$',api_consulta_producto),	
	url(r'^carrito_compras/$',api_consulta_carrito_compras),	
	url(r'^elimina_prod_carrito/$',api_elimina_carrito_compras),		
	url(r'^direccion_envio/$',api_direccion_envio),	
	url(r'^busca_productos/$',api_busqueda_productos),		
	url(r'^cont_prod_carrito/$',api_cont_productos_carrito),		
	url(r'^guarda_venta/$',api_crea_venta),		


]

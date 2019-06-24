from django.conf.urls import url
from seguridad.views import Login,bienvenidos,api_alta_cliente,api_login_usuario,api_esta_logueado
from seguridad.views import api_direccion_envio_temporal,api_e_mail_notificacion

app_name="seguridad"

urlpatterns=[
	url(r'^$', Login.as_view(), name="login"), 
	url(r'^bienvenidos$',bienvenidos,name="bienvenidos"),	
	#apis
	url(r'^alta_cliente/$',api_alta_cliente,name="alta_cliente"),
	url(r'^login_usr/$',api_login_usuario,name="login_usr"),
	url(r'^valida_logueado/$',api_esta_logueado,name="esta_logueado"),
	url(r'^direccion_envio_temporal/$',api_direccion_envio_temporal,name="direccion_envio_temporal"),
	url(r'^e_mail_notificacion/$',api_e_mail_notificacion,name="e_mail_notificacion"),


]


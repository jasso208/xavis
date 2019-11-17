from django.conf.urls import url
from seguridad.views import Login,bienvenidos,api_alta_cliente,api_login_usuario,api_esta_logueado
from seguridad.views import api_direccion_envio_temporal,api_e_mail_notificacion,api_actualiza_contraseña
from seguridad.views import api_envia_token,api_cambia_psw_token,api_kill_session
from seguridad.views import api_reinicia_direccion_temporal,api_consulta_ventas_invitado

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
	url(r'^actualiza_psw/$',api_actualiza_contraseña,name="actualiza_psw"),
	url(r'^envia_token/$',api_envia_token,name="envia_token"),
	url(r'^cambia_psw_token/$',api_cambia_psw_token,name="cambia_psw_token"),
	url(r'^kill_session/$',api_kill_session,name="kill_session"),
	url(r'^reinicia_direccion_envio/$',api_reinicia_direccion_temporal,name="reinicia_direccion_envio"),
	url(r'^get_ventas_invitados/$',api_consulta_ventas_invitado,name="get_ventas_invitados"),



]


from django.conf.urls import url
from seguridad.views import Login,bienvenidos,api_alta_cliente,api_login_usuario,api_esta_logueado
from seguridad.views import api_direccion_envio_temporal,api_e_mail_notificacion,api_actualiza_contrasena
from seguridad.views import api_envia_token,api_cambia_psw_token,api_kill_session
from seguridad.views import api_reinicia_direccion_temporal,cerrar_session
from seguridad.views import admin_user,permisos,admin_productos,admin_catalogos,admin_ventas,alta_usuario
from seguridad.views import consulta_usuarios,admin_perfil,cambio_psw_usr,admin_cajas,admin_reportes
from seguridad.views import admin_empenos,cambio_sucursal

app_name="seguridad"

urlpatterns=[
	url(r'^$',Login, name="login"), 
	url(r'^cerrar_session$',cerrar_session,name="cerrar_session"),		
	url(r'^admin_user$',admin_user,name="admin_user"),		
	url(r'^admin_perfil$',admin_perfil,name="admin_perfil"),		
	url(r'^cambio_psw_usr$',cambio_psw_usr,name="cambio_psw_usr"),	
	url(r'^permisos$',permisos,name="permisos"),	
	url(r'^admin_productos$',admin_productos,name="admin_productos"),	
	url(r'^admin_ventas$',admin_ventas,name="admin_ventas"),	
	url(r'^admin_catalogos$',admin_catalogos,name="admin_catalogos"),
	url(r'^admin_cajas$',admin_cajas,name="admin_cajas"),
	url(r'^admin_reportes$',admin_reportes,name="admin_reportes"),
	url(r'^admin_empenos$',admin_empenos,name="admin_empenos"),
	url(r'^cambio_sucursal$',cambio_sucursal,name="cambio_sucursal"),



	url(r'^modifica_usr/(?P<id>\d+)/$',alta_usuario,name="modifica_usr"),	
	url(r'^alta_usuario/$',alta_usuario,name="alta_usuario"),

	url(r'^consulta_usuarios$',consulta_usuarios,name="consulta_usuarios"),	
	url(r'^bienvenidos$',bienvenidos,name="bienvenidos"),	
	
	
	#apis
	url(r'^alta_cliente/$',api_alta_cliente,name="alta_cliente"),
	url(r'^login_usr/$',api_login_usuario,name="login_usr"),
	url(r'^valida_logueado/$',api_esta_logueado,name="esta_logueado"),
	url(r'^direccion_envio_temporal/$',api_direccion_envio_temporal,name="direccion_envio_temporal"),
	url(r'^e_mail_notificacion/$',api_e_mail_notificacion,name="e_mail_notificacion"),
	url(r'^actualiza_psw/$',api_actualiza_contrasena,name="actualiza_psw"),
	url(r'^envia_token/$',api_envia_token,name="envia_token"),
	url(r'^cambia_psw_token/$',api_cambia_psw_token,name="cambia_psw_token"),
	url(r'^kill_session/$',api_kill_session,name="kill_session"),
	url(r'^reinicia_direccion_envio/$',api_reinicia_direccion_temporal,name="reinicia_direccion_envio"),



]




from django.conf.urls import include, url
from .views import *
from empenos.apis import *

app_name="empenos"

urlpatterns=[
	#formularios
	url(r'^abrir_caja/$',abrir_caja,name="abrir_caja"),
	url(r'^otros_ingresos/$',otros_ingresos,name="otros_ingresos"),
	url(r'^retiro_efectivo/$',retiro_efectivo,name="retiro_efectivo"),
	url(r'^corte_caja/$',corte_caja,name="corte_caja"),
	url(r'^reportes_caja/$',reportes_caja,name="reportes_caja"),
	url(r'^nvo_empeno/$',nvo_empeno,name="nvo_empeno"),
	url(r'^alta_cliente/$',alta_cliente,name="alta_cliente"),
	url(r'^edita_cliente/(?P<id_cliente>\w+)/$',alta_cliente,name="edita_cliente"),
	url(r'^imprime_boleta/$',imprime_boleta,name="imprime_boleta"),
	url(r'^consulta_boleta/$',consulta_boleta,name="consulta_boleta"),
	url(r'^refrendo/(?P<id_boleta>\w+)/$',refrendo,name="refrendo"),
	url(r'^refrendo_plazo_mensual/(?P<id_boleta>\w+)/$',refrendo_plazo_mensual,name="refrendo_plazo_mensual"),
	url(r'^imprime_abono/$',imprime_abono,name="imprime_abono"),
	url(r'^re_imprimir_boleta/(?P<id_boleta>\w+)/$',re_imprimir_boleta,name="re_imprimir_boleta"),
	url(r'^re_imprimir_abono/(?P<id_abono>\w+)/$',re_imprimir_abono,name="re_imprimir_abono"),
	url(r'^rep_flujo_caja/$',rep_flujo_caja,name="rep_flujo_caja"),
	url(r'^elimina_costo_extra/$',elimina_costo_extra,name="elimina_costo_extra"),
	url(r'^admin_kilataje$',admin_kilataje,name="admin_kilataje"),
	url(r'^venta_granel$',venta_granel,name="venta_granel"),
	url(r'^imprime_venta_granel$',imprime_venta_granel,name="imprime_venta_granel"),
	url(r'^consulta_venta$',consulta_venta,name="consulta_venta"),
	url(r'^re_imprimir_venta/(?P<id_venta>\w+)/$',re_imprimir_venta,name="re_imprimir_venta"),

	url(r'^consulta_abono$',consulta_abono,name="consulta_abono"),

	url(r'^cierra_caja/$',api_cierra_caja,name="cierra_caja"),
	url(r'^envia_token/$',api_envia_token),	
	url(r'^api_consulta_corte_caja/$',api_consulta_corte_caja),	
	url(r'^re_abre_caja/$',api_re_abre_caja),
	url(r'^api_tipo_producto/$',api_tipo_producto),	
	url(r'^api_consulta_linea/$',api_consulta_linea),	
	url(r'^api_consulta_sublinea/$',api_consulta_sublinea),	
	url(r'^api_consulta_marcas/$',api_consulta_marcas),	
	url(r'^api_consulta_kilataje/$',api_consulta_kilataje),	
	url(r'^api_consulta_costo_kilataje/$',api_consulta_costo_kilataje),	
	url(r'^api_guarda_producto_temporal/$',api_guarda_producto_temporal),	
	url(r'^api_consulta_cotizacion/$',api_consulta_cotizacion),	
	url(r'^api_elimina_producto_cotizacion/$',api_elimina_producto_cotizacion),	
	url(r'^api_consulta_cliente/$',api_consulta_cliente),	
	url(r'^api_limpia_cotizacion/$',api_limpia_cotizacion),	
	url(r'^api_consulta_boleta/$',api_consulta_boleta),	
	url(r'^api_simula_refrendo/$',api_simula_refrendo),	
	url(r'^api_simula_refrendo_mensual/$',api_simula_refrendo_mensual),	
	url(r'^api_consulta_sucurales_usuario/$',api_consulta_sucurales_usuario),	
	url(r'^api_reg_costo_reimpresion/$',api_reg_costo_reimpresion),	
	url(r'^api_job_diario/$',api_job_diario),		
	url(r'^api_notificacion_cajas_abiertas/$',api_notificacion_cajas_abiertas,name="api_notificacion_cajas_abiertas"),
	url(r'^api_agrega_marca/$',api_agrega_marca,name="api_agrega_marca"),
	url(r'^api_elimina_costo_extra/$',api_elimina_costo_extra,name="api_elimina_costo_extra"),
	url(r'^api_elimina_costo_kilataje/$',api_elimina_costo_kilataje,name="api_elimina_costo_kilataje"),
	url(r'^api_agregar_kilataje/$',api_agregar_kilataje,name="api_agregar_kilataje"),
	url(r'^api_agrega_boleta_venta_granel/$',api_agrega_boleta_venta_granel,name="api_agrega_boleta_venta_granel"),
	url(r'^api_agrega_importe_real_venta/$',api_agrega_importe_real_venta,name="api_agrega_importe_real_venta"),

]

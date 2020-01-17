from django.conf.urls import include, url
from contabilidad import views

app_name="contabilidad"

urlpatterns=[
	#formularios
	url(r'^concepto_ingreso/$',views.registro_concepto_ingreso,name="concepto_ingreso"),
	url(r'^concepto_gasto/$',views.registro_concepto_gasto,name="concepto_gasto"),
	url(r'^registro_ingreso/$',views.registro_movs_ingreso,name="registro_ingreso"),
	url(r'^reporte_ingresos/$',views.reporte_ingresos,name="reporte_ingresos"),
	url(r'^registro_gasto/$',views.registro_movs_gasto,name="registro_gasto"),
	url(r'^reporte_gastos/$',views.reporte_gastos,name="reporte_gastos"),
	
]
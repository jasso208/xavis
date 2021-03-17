from django.contrib import admin
from .models import Tipo_Movimiento,Perfil,Sucursal,User_2,Sucursales_Regional,Cajas,Otros_Ingresos,Retiro_Efectivo,Token,Control_Folios
from .models import Tipo_Producto,Linea,Sub_Linea,Marca,Costo_Kilataje,Empenos_Temporal,Joyeria_Empenos_Temporal,Plazo,Cliente
from .models import Boleta_Empeno,Det_Boleto_Empeno,Estatus_Boleta,Imprimir_Boletas,Tipo_Pago,Pagos,Dia_No_Laboral,Pagos_Temp,Rel_Abono_Capital,Rel_Abono_Pago
from .models import Abono,Imprime_Abono,Periodo,Tipo_Periodo,Tipo_Kilataje,Venta_Temporal,Venta_Granel,Det_Venta_Granel,Imprime_Venta_Granel
from .models import Venta_Temporal_Piso,Porcentaje_Sobre_Avaluo,Imprime_Venta_Piso,Venta_Piso,Det_Venta_Piso
from .models import Estatus_Apartado,Abono_Apartado,Apartado,Imprime_Apartado,Concepto_Retiro,Configuracion_Interes_Empeno
from .models import Pagos_No_Usados,Pagos_Com_Pg_No_Usados,Historico_Estatus_Cartera,Empresa,Min_Apartado,Configuracion_Contenido_Impresion
# Register your models here.


admin.site.register(Concepto_Retiro)
admin.site.register(Tipo_Movimiento)
admin.site.register(Perfil)
admin.site.register(Sucursal)
admin.site.register(User_2)
admin.site.register(Sucursales_Regional)
admin.site.register(Cajas)
admin.site.register(Otros_Ingresos)
admin.site.register(Retiro_Efectivo)
admin.site.register(Token)
admin.site.register(Control_Folios)

admin.site.register(Tipo_Producto)
admin.site.register(Linea)
admin.site.register(Sub_Linea)
admin.site.register(Marca)
admin.site.register(Costo_Kilataje)
admin.site.register(Empenos_Temporal)
admin.site.register(Joyeria_Empenos_Temporal)
admin.site.register(Plazo)
admin.site.register(Cliente)
admin.site.register(Boleta_Empeno)
admin.site.register(Det_Boleto_Empeno)
admin.site.register(Estatus_Boleta)
admin.site.register(Imprimir_Boletas)
admin.site.register(Tipo_Pago)
admin.site.register(Pagos)
admin.site.register(Rel_Abono_Capital)
admin.site.register(Rel_Abono_Pago)
admin.site.register(Abono)
admin.site.register(Imprime_Abono)
admin.site.register(Periodo)
admin.site.register(Tipo_Periodo)
admin.site.register(Tipo_Kilataje)
admin.site.register(Venta_Temporal)
admin.site.register(Venta_Granel)
admin.site.register(Det_Venta_Granel)
admin.site.register(Imprime_Venta_Granel)
admin.site.register(Venta_Temporal_Piso)
admin.site.register(Porcentaje_Sobre_Avaluo)
admin.site.register(Imprime_Venta_Piso)
admin.site.register(Venta_Piso)
admin.site.register(Det_Venta_Piso)

admin.site.register(Estatus_Apartado)
admin.site.register(Abono_Apartado)
admin.site.register(Apartado)
admin.site.register(Imprime_Apartado)
admin.site.register(Configuracion_Interes_Empeno)
admin.site.register(Pagos_No_Usados)
admin.site.register(Pagos_Com_Pg_No_Usados)
admin.site.register(Historico_Estatus_Cartera)
admin.site.register(Empresa)
admin.site.register(Dia_No_Laboral)

admin.site.register(Min_Apartado)
admin.site.register(Configuracion_Contenido_Impresion)




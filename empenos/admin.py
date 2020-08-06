from django.contrib import admin
from .models import Tipo_Movimiento,Perfil,Sucursal,User_2,Sucursales_Regional,Cajas,Otros_Ingresos,Retiro_Efectivo,Token,Control_Folios
from .models import Tipo_Producto,Linea,Sub_Linea,Marca,Costo_Kilataje,Empenos_Temporal,Joyeria_Empenos_Temporal,Plazo,Cliente
from .models import Boleta_Empeno,Det_Boleto_Empeno,Estatus_Boleta,Imprimir_Boletas,Tipo_Pago,Pagos,Dia_No_Laboral,Pagos_Temp,Rel_Abono_Capital,Rel_Abono_Pago
from .models import Abono,Imprime_Abono,Periodo,Tipo_Periodo
# Register your models here.

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







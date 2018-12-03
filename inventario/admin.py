from django.contrib import admin
from .models import Estatus,Productos,Tallas,Atributos,Img_Producto,Productos_Relacionados,Carrito_Compras
from .models import Municipio,Estado,Pais,Direccion_Envio,Categorias,Rel_Producto_Categoria
from .models import Venta,Detalle_Venta,Direccion_Envio_Venta

admin.site.register(Estatus)
admin.site.register(Productos)
admin.site.register(Tallas)
admin.site.register(Atributos)
admin.site.register(Img_Producto)
admin.site.register(Productos_Relacionados)
admin.site.register(Carrito_Compras)
admin.site.register(Municipio)
admin.site.register(Estado)
admin.site.register(Pais)
admin.site.register(Direccion_Envio)
admin.site.register(Categorias)
admin.site.register(Rel_Producto_Categoria)
admin.site.register(Venta)
admin.site.register(Detalle_Venta)
admin.site.register(Direccion_Envio_Venta)
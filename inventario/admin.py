from django.contrib import admin
from .models import Estatus,Productos,Tallas,Atributos,Img_Producto,Productos_Relacionados
from .models import Municipio,Estado,Pais,Categorias,Rel_Producto_Categoria


admin.site.register(Estatus)
admin.site.register(Productos)
admin.site.register(Tallas)
admin.site.register(Atributos)
admin.site.register(Img_Producto)
admin.site.register(Productos_Relacionados)
admin.site.register(Municipio)
admin.site.register(Estado)
admin.site.register(Pais)
admin.site.register(Categorias)
admin.site.register(Rel_Producto_Categoria)

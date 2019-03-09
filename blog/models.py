from django.db import models
from django.utils import timezone
from datetime import datetime
from inventario.models import Productos

class Estatus_Blog(models.Model):
	estatus=models.CharField(max_length=20,null=False)

	def __str__(self):
		return self.estatus
	
class Blog(models.Model):
	nombre_blog=models.CharField(max_length=200,null=False)
	contenido_blog=models.TextField(null=False)
	imagen_blog=models.CharField(max_length=50,null=True)
	fecha=models.DateTimeField(default=timezone.now)
	id_estatus=models.ForeignKey(Estatus_Blog,on_delete=models.PROTECT)
	
	def __str__(self):
		return self.nombre_blog

class Productos_Relacionados(models.Model):
	id_blog=models.ForeignKey(Blog,on_delete=models.PROTECT,related_name='blog')
	id_producto_relacionado=models.ForeignKey(Productos,on_delete=models.PROTECT,related_name='id_producto_relacionado')
	
	class Meta:
		unique_together=('id_blog','id_producto_relacionado')

class Rel_Blog_Blog(models.Model):
	id_blog=models.ForeignKey(Blog,on_delete=models.PROTECT,related_name="id_blog")
	id_blog_relacionado=models.ForeignKey(Blog,on_delete=models.PROTECT,related_name="id_blog_relacionado")
	

	class Meta:
		unique_together=('id_blog','id_blog_relacionado')
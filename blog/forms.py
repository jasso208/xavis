from django import forms
from .models import Blog,Estatus_Blog

class Blog_Form(forms.ModelForm):
	class Meta:
		model=Blog
		fields=("nombre_blog","id_estatus","imagen_blog","autor","puesto_autor")
		
class Busqueda_Blog_Form(forms.Form):	
	fecha_inicial=forms.DateTimeField()
	fecha_final=forms.DateTimeField()
	id_estatus=forms.ModelChoiceField(queryset=Estatus_Blog.objects.all())
	
	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		# asi vuelves tus campos no requeridos
		self.fields['fecha_inicial'].required = False 
		self.fields['fecha_final'].required = False
		self.fields['id_estatus'].required = False
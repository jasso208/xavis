from .models import Productos,Atributos,Tallas,Proveedor,Estatus,Categorias
from django import forms
from django.forms.models import inlineformset_factory

class Proveedores_Form(forms.ModelForm):
	class Meta:
		model=Proveedor
		fields=("proveedor","id_estatus",)

class Productos_Form(forms.ModelForm):
	class Meta:
		model=Productos
		fields=('nombre','precio_ml','porcentaje_ganancia','porcentaje_ganancia_ml','desc_producto','precio','descuento','id_proveedor','marca','id_estatus','clave_prod_proveedor','precio_proveedor',"publicado_ml",)

class Busqueda_Producto_Form(forms.Form):	
	id_proveedor=forms.ModelChoiceField(queryset=Proveedor.objects.all())
	id_estatus=forms.ModelChoiceField(queryset=Estatus.objects.all())
	id_producto=forms.IntegerField()	
	clave_proveedor=forms.CharField(max_length=20)
	pml = forms.ModelChoiceField(queryset=Estatus.objects.all())

	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		# asi vuelves tus campos no requeridos
		self.fields['id_proveedor'].required = False 
		self.fields['id_estatus'].required = False
		self.fields['id_producto'].requiered=False
		self.fields['clave_proveedor'].requiered=False		
		self.fields['pml'].requiered=False
		
class Consulta_Existencia_Form(forms.Form):
	producto=forms.CharField(max_length=60)
	id_producto=forms.IntegerField()
	clave_proveedor=forms.CharField(max_length=20)

	def __init__(self,*args,**kwargs):
		super(self.__class__,self).__init__(*args,**kwargs)
		self.fields['producto'].requiered=False
		self.fields['id_producto'].requiered=False
		self.fields['clave_proveedor'].requiered=False


class Busca_Proveedores_Form(forms.Form):
	nombre_proveedor=forms.CharField(max_length=50)
	
	def __init__(self,*args,**kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		self.fields['nombre_proveedor'].required=False
		
class Categorias_Form(forms.ModelForm):
	class Meta:
		model=Categorias
		fields=("categoria_1","categoria_2","categoria",)
		
class Busca_X_Clave_Prod_Prov_Form(forms.Form):
	clave_prod_proveedor=forms.CharField(max_length=20)


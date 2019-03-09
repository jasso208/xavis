from django import forms
from .models import Venta,Estatus_Venta
class Busqueda_Venta_Form(forms.Form):
	fecha_inicial=forms.DateTimeField()
	fecha_final=forms.DateTimeField()
	id_estatus_venta=forms.ModelChoiceField(queryset=Estatus_Venta.objects.all())
	
	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		# asi vuelves tus campos no requeridos
		self.fields['fecha_final'].required = False 
		self.fields['fecha_inicial'].required = False
		self.fields['id_estatus_venta'].required = False
		
		
class Venta_Form(forms.ModelForm):
	class Meta:
		model=Venta
		fields=("fecha","sub_total","descuento","iva","total","id_estatus_venta","link_seguimiento")
	

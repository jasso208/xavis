from django import forms
from .models import Venta,Estatus_Venta,Detalle_Venta,Medio_Venta


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
		fields=("fecha","comision","costo_envio","sub_total","descuento","iva","total","id_medio_venta","id_estatus_venta","link_seguimiento","forma_pago",)
	
class Det_Venta_Form(forms.ModelForm):
	class Meta:
		model=Detalle_Venta
		fields=("id_venta","id_producto","cantidad","talla","precio_unitario","descuento","iva","precio_total",)

class Medio_Venta_Form(forms.ModelForm):
	class Meta:
		model=Medio_Venta
		fields=("desc_medio",)
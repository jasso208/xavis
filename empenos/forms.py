from django import forms
from django.forms.models import inlineformset_factory
from empenos.models import Cajas,Otros_Ingresos,Retiro_Efectivo,Tipo_Movimiento,Plazo,Cliente,Sucursal,Estatus_Boleta
from datetime import date, datetime, time
from django.utils import timezone
class Abre_Caja_Form(forms.ModelForm):
	class Meta:
		model=Cajas
		fields=('sucursal','importe','tipo_movimiento','usuario',"diferencia",)

class Otros_Ingresos_Form(forms.ModelForm):
	class Meta:
		model=Otros_Ingresos
		fields=('tipo_movimiento','importe','comentario',)

class Retiro_Efectivo_Form(forms.ModelForm):
	class Meta:
		model=Retiro_Efectivo
		fields=('tipo_movimiento','importe','comentario','token',)


class Cierra_Caja_Form(forms.Form):
	centavos_10=forms.IntegerField()
	centavos_50=forms.IntegerField()
	pesos_1=forms.IntegerField()
	pesos_2=forms.IntegerField()
	pesos_5=forms.IntegerField()
	pesos_10=forms.IntegerField()
	pesos_20=forms.IntegerField()
	pesos_50=forms.IntegerField()
	pesos_100=forms.IntegerField()
	pesos_200=forms.IntegerField()
	pesos_500=forms.IntegerField()
	pesos_1000=forms.IntegerField()
	diferencia=forms.IntegerField()
	real_efectivo=forms.IntegerField()
	token=forms.IntegerField()
	comentario=forms.CharField(widget=forms.Textarea)

class Refrendo_Form(forms.Form):
	importe_abono=forms.IntegerField()

class Refrendo_Mensual_Form(forms.Form):
	total_refrendo=forms.IntegerField()
	descuento=forms.IntegerField()

class Reportes_Caja_Form(forms.Form):
	id_tipo_mov=forms.ModelChoiceField(queryset=Tipo_Movimiento.objects.filter().exclude(id=4).exclude(id=5))
	fecha_inicial=forms.DateTimeField(initial=timezone.now())
	fecha_final=forms.DateTimeField(initial=timezone.now())

class Buscar_Ventas_Form(forms.Form):
	fecha_inicial=forms.DateTimeField(initial=timezone.now())
	fecha_final=forms.DateTimeField(initial=timezone.now())

class Costo_Extra_Form(forms.Form):
	sucursal=forms.ModelChoiceField(queryset=Sucursal.objects.all())


class Consulta_Abono_Form(forms.Form):
	sucursal=forms.ModelChoiceField(queryset=Sucursal.objects.all())
	fecha_inicial=forms.DateTimeField()
	fecha_final=forms.DateTimeField()
	
	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		# asi vuelves tus campos no requeridos
		self.fields['sucursal'].required = False		
		self.fields['fecha_inicial'].required = False
		self.fields['fecha_final'].required = False
		
class Consulta_Boleta_Form(forms.Form):
	sucursal=forms.ModelChoiceField(queryset=Sucursal.objects.all())
	cliente=forms.CharField(max_length=30)
	boleta=forms.IntegerField()
	fecha_inicial=forms.DateTimeField()
	fecha_final=forms.DateTimeField()
	estatus_boleta=forms.ModelChoiceField(queryset=Estatus_Boleta.objects.all())

	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		# asi vuelves tus campos no requeridos
		self.fields['cliente'].required = False
		self.fields['boleta'].required = False		
		self.fields['fecha_inicial'].required = False
		self.fields['fecha_final'].required = False
		self.fields['estatus_boleta'].required = False

class Flujo_Caja_Form(forms.Form):
	sucursal=forms.ModelChoiceField(queryset=Sucursal.objects.all())	
	fecha_inicial=forms.DateTimeField()
	fecha_final=forms.DateTimeField()
		
	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		# asi vuelves tus campos no requeridos
		self.fields['sucursal'].required = False

class Nuevo_Empeno_Form(forms.Form):
	plazo=forms.ModelChoiceField(queryset=Plazo.objects.all())
	nombre_cotitular=forms.CharField(max_length=30)
	apellido_paterno=forms.CharField(max_length=30)
	apellido_materno=forms.CharField(max_length=30)
	cliente=forms.ModelChoiceField(queryset=Cliente.objects.all().order_by('apellido_p'))

	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		# asi vuelves tus campos no requeridos
		self.fields['nombre_cotitular'].required = False
		self.fields['apellido_paterno'].required = False
		self.fields['apellido_materno'].required = False

class Cliente_Form(forms.ModelForm):
	class Meta:
		model=Cliente
		fields=('nombre','apellido_p','apellido_m','genero','estado_civil','codigo_postal','calle','numero_interior','numero_exterior','colonia','ciudad','estado','pais','telefono_fijo','telefono_celular','usuario',)


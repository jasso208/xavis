from django import forms
from django.forms.models import inlineformset_factory
from .models import Concepto_Ingreso,Concepto_Gasto,Movs_Ingreso,Movs_Gasto

class Concepto_Ingreso_form(forms.ModelForm):
    class Meta:
        model=Concepto_Ingreso
        fields=("desc_concepto_ingreso",)


class Concepto_Gasto_Form(forms.ModelForm):
    class Meta:
        model=Concepto_Gasto
        fields=("desc_concepto_gasto",)

class Movs_Ingreso_Form(forms.ModelForm):
    class Meta:
        model=Movs_Ingreso
        fields=("id_concepto_ingreso","descripcion","importe","fecha",)

class Movs_Gasto_Form(forms.ModelForm):
    class Meta:
        model=Movs_Gasto
        fields=("id_concepto_gasto","descripcion","importe","fecha",)

class Busca_Movs_Ingreso_Form(forms.Form):
    fecha_inicial=forms.DateTimeField()
    fecha_final=forms.DateTimeField()

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # asi vuelves tus campos no requeridos
        self.fields['fecha_final'].required = False 
        self.fields['fecha_inicial'].required = False


class Busca_Movs_Gasto_Form(forms.Form):
    fecha_inicial=forms.DateTimeField()
    fecha_final=forms.DateTimeField()

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # asi vuelves tus campos no requeridos
        self.fields['fecha_final'].required = False 
        self.fields['fecha_inicial'].required = False
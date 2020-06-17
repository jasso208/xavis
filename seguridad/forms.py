from django import forms
from django.contrib.auth.models  import Permission,User

class Login_Form(forms.Form):
	usuario=forms.CharField(max_length=30)
	password=forms.CharField(max_length=30,widget=forms.PasswordInput)


class Busca_Usuario_Form(forms.Form):
	username=forms.CharField(max_length=30)

	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		# asi vuelves tus campos no requeridos
		self.fields['username'].required = False

class Cambia_Psw_Form(forms.Form):
	psw=forms.CharField(widget=forms.PasswordInput)
	

class Permisos_Form(forms.ModelForm):
	class Meta:
		model=Permission
		fields=("name","content_type","codename")

class User_Form(forms.ModelForm):
	class Meta:
		model=User
		fields=("username","first_name","last_name","email","password","groups","is_staff","is_active","is_superuser")
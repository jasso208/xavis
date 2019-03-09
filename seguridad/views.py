from django.views.generic.edit import FormView
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth import logout
from django.urls import reverse

class Login(FormView):
	template_name="login.html"
	form_class=AuthenticationForm
	success_url="/bienvenidos"
	
	def dispatch(self,request,*args,**kwargs):
		if request.user.is_authenticated:
			return HttpResponseRedirect("/bienvenidos")
		else:
			return super(Login,self).dispatch(request,*args,**kwargs)
	
	def form_valid(self,form):
		login(self.request,form.get_user())
		return super(Login,self).form_valid(form)
		

	
def bienvenidos(request):
	return render(request,'seguridad/bienvenidos.html',{})

from django.conf.urls import url
from seguridad.views import Login,bienvenidos
app_name="seguridad"

urlpatterns=[
	url(r'^$', Login.as_view(), name="login"), 
	url(r'^bienvenidos$',bienvenidos,name="bienvenidos"),	

]

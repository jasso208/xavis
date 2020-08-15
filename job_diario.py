import requests
# Creamos la peticion HTTP con GET:
r = requests.get("https://empeno.jassdel.com/empenos/api_job_diario/")
# Imprimimos el resultado si el codigo de estado HTTP es 200 (OK):
if r.status_code == 200:
	print("Exito")
else:
	print("Fallo")





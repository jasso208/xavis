import requests
# Creamos la petición HTTP con GET:
r = requests.get("http://127.0.0.1:8000/empenos/api_job_diario/")
# Imprimimos el resultado si el código de estado HTTP es 200 (OK):
if r.status_code == 200:
	print("Exito")
else:
	print("Fallo")





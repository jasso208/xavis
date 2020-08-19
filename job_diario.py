import requests

print(date.today())

print("Iniciamos proceso boletas vencidas")
#ejecutamos el proceso para detectar boletas o periodos vencidos.
#https://empeno.jassdel.com/
r = requests.get("http://127.0.0.1:8000/empenos/api_job_diario/")
# Imprimimos el resultado si el código de estado HTTP es 200 (OK):
if r.status_code == 200:
	print("Exito")
else:
	print("Fallo")


print("Iniciamos proceso envio reporte cajas abiertas")
#https://empeno.jassdel.com/
r = requests.get("http://127.0.0.1:8000/empenos/api_notificacion_cajas_abiertas/")

if r.status_code == 200:
	print("Exito")
else:
	print("Fallo")





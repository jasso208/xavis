import requests

print("iniciamos proceso de respaldo de base de datos")
r = requests.get("https://empeno.jassdel.com/empenos/api_backup")

print("Iniciamos proceso boletas vencidas")
#ejecutamos el proceso para detectar boletas o periodos vencidos.
#https://empeno.jassdel.com/
r = requests.get("https://empeno.jassdel.com/empenos/api_job_diario/")
# Imprimimos el resultado si el codigo de estado HTTP es 200 (OK):

if r.status_code == 200:
	print("Exito")
else:
	print("Fallo")


print("Iniciamos proceso envio reporte cajas abiertas")
#https://empeno.jassdel.com/
r = requests.get("https://empeno.jassdel.com/empenos/api_notificacion_cajas_abiertas/")

if r.status_code == 200:
	print("Exito")
else:
	print("Fallo")

print("Guardamos el estatus de la cartera al ciere del dia")

#https://empeno.jassdel.com/
r = requests.get("https://empeno.jassdel.com/empenos/api_guarda_estatus_cartera/")

if r.status_code == 200:
	print("Exito")
else:
	print("Fallo")




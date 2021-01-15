from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
import json
from empenos.models import *
from django.db import transaction

@api_view(["POST","PUT"])
@transaction.atomic
def api_usuario(request):
	if request.method == "POST":
		id_sucursal = request.data["id_sucursal"]
		id_perfil = request.data["id_perfil"]
		user_name = request.data["user_name"]
		first_name = request.data["first_name"]
		last_name = request.data["last_name"]
		id_usuario_alta = request.data["id_usuario_alta"]

		resp = []
		try:

			respuesta = User_2.fn_alta_usuario(user_name,first_name,last_name,id_sucursal,id_perfil,id_usuario_alta)
			if not respuesta[0]:
				resp.append({"estatus":"0","msj":respuesta[1]})		
				transaction.set_rollback(True)	
			else:
				resp.append({"estatus":"1","msj":respuesta[1]})
		except Exception as e:
			print(e)
			transaction.set_rollback(True)	
			resp.append({"estatus":"0","msj":"Error al dar de alta el usuario."})
		return Response(json.dumps(resp))
	elif request.method == "PUT":
		id_sucursal = request.data["id_sucursal"]
		id_perfil = request.data["id_perfil"]
		user_name = request.data["user_name"]
		first_name = request.data["first_name"]
		last_name = request.data["last_name"]
		id_usuario_alta = request.data["id_usuario_alta"]
		activo = request.data["activo"]

		resp = []
		try:

			respuesta = User_2.fn_edita_usuario(user_name,first_name,last_name,id_sucursal,id_perfil,id_usuario_alta,activo)
			if not respuesta[0]:
				resp.append({"estatus":"0","msj":respuesta[1]})		
				transaction.set_rollback(True)	
			else:
				resp.append({"estatus":"1","msj":respuesta[1]})
		except Exception as e:
			print(e)
			transaction.set_rollback(True)	
			resp.append({"estatus":"0","msj":"Error al actualizar el usuario."})
		return Response(json.dumps(resp))

@api_view(["PUT"])
def api_reinicia_psw(request):
	resp = []
	try:
		user_name = request.data["user_name"]

		user = User.objects.get(username = user_name)

		user.set_password("12345")
		user.save()

		resp.append({"estatus":"1","msj":"La contraseña se reinicio correctamente."})
	except:
		resp.append({"estatus":"0","msj":"Error al reiniciar la contraseña"})
	return Response(json.dumps(resp))

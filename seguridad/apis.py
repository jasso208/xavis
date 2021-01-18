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


@api_view(["POST","PUT"])
def api_permisos_usuario(request):
	resp = []
	if request.method == "POST":
		try:
		
			id_usuario = request.data["id_usuario"]
		
			id_item_menu = request.data["id_item_menu"]
		
			id_usuario_asigna = request.data["id_usuario_asigna"]
			
			#usuario al que se le daran permisos
			usuario = User_2.objects.get(user__id = id_usuario)
			
			respuesta = usuario.fn_agrega_acceso_a_vista(id_item_menu,id_usuario_asigna)
		

			if respuesta[0]:#se actualizo correctamente
				resp.append({"estatus":"1","msj":respuesta[1]})
			else:
				resp.append({"estatus":"0","msj":respuesta[1]})

		except Exception as e:
			print(e)
			resp.append({"estatus":"0","msj":"Error al actalizar los permisos."})
		return Response(json.dumps(resp))
	if request.method == "PUT":
			id_usuario = request.data["id_usuario"]		
			id_item_menu = request.data["id_item_menu"]
			#usuario al que se le daran permisos
			usuario = User_2.objects.get(user__id = id_usuario)
			
			respuesta = usuario.fn_remover_acceso_a_vista(id_item_menu)

			if respuesta[0]:#se actualizo correctamente
				resp.append({"estatus":"1","msj":respuesta[1]})
			else:
				resp.append({"estatus":"0","msj":respuesta[1]})

			return Response(json.dumps(resp))


			
@api_view(["GET"])
def api_consulta_usuario(request):
	resp = []
	try:
		username = request.GET.get("username")
		usuario = User.objects.get(username = username)
		resp.append({"estatus":"1","nombre_usuario":usuario.first_name + " " + usuario.last_name,"id_usuario_a_modificar":usuario.id})
	except:
		resp.append({"estatus":"0","msj":"No existe usuario con el nombre de usuario indicado."})
		return Response(json.dumps(resp))
	#obtenemos la lista de los permisos del usuario
	permisos = User_2.objects.get(user = usuario).fn_consulta_permisos()

	resp.append(permisos)
	return Response(json.dumps(resp))



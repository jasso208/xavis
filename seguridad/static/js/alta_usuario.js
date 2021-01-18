
var id_usuario_alta;
var csrf_token;
var ip_local;
var is_edicion;
var activo;
$(document).ready(
	function()
	{
		$("#btn_guardar").click(
			function()
			{
				return fn_valida_formulario();
			}

		);

		$("#btn_aceptar_error").click(
				function()
				{
					$(".cls_error").hide();
				}
			);
		$("#btn_reinicia_psw").click(
				function()
				{
					$(".cls_confirma_reinicio_psw").show();
				}
			);
		$("#fondo_confirmacion,#btn_cancelar_confirmacion").click(
				function()
				{
					$(".cls_confirma_reinicio_psw").hide();
				}
			);
		$("#btn_confirmar_reset_pws").click(
				function()
				{
					fn_reinicia_psw();
				}
			);

	}
	);

function fn_inicio(is_edit,id_usr,token,ip,user_name,first_name,last_name,id_perfil,id_sucursal,act)
{
	is_edicion = is_edit;
	id_usuario_alta = id_usr;
	csrf_token = token;
	ip_local = ip;
	activo = act;

	if(is_edicion == "0")
	{
		$("#id_username").val("");
		$("#id_password").show();
		$("#id_username").prop("readonly",false);	
	}
	else
	{

		$("#id_password").hide();	
		$("#id_username").prop("readonly",true);	

	}
	

	$("#id_username").val(user_name);	
	$("#id_first_name").val(first_name);	
	$("#id_last_name").val(last_name);	
	$("#id_perfil").val(id_perfil);	
	$("#id_sucursal").val(id_sucursal);	
	$(".cls_confirma_reinicio_psw").hide();

	
	if (activo == "True")
	{
	
		$("#id_activo").prop("checked",true);		
	}
	else
	{
		
		$("#id_activo").prop("checked",false);				
	}
	

	$(".help-block").hide();
	$(".cls_error").hide();
	$(".cls_exito").hide();

	$("#fondo_preloader").hide();

}

function fn_valida_formulario()
{
	
	$("#fondo_preloader").show();
	if($("#id_username").val() == "")
	{
		$(".cls_error").show();
		$("#msj_notificacion").text("El nombre de usuario es requerido.");
		$("#fondo_preloader").hide();
		return false;
	}
	if($("#id_first_name").val() == "")
	{
		$(".cls_error").show();
		$("#msj_notificacion").text("El nombre del usuario es requerido.");
		$("#fondo_preloader").hide();
		return false;	
	}

	if($("#id_last_name").val() == "")
	{
		$(".cls_error").show();
		$("#msj_notificacion").text("Debe indicar al menos el apellido paterno.");
		$("#fondo_preloader").hide();
		return false;	
	}

	if($("#id_sucursal").val() == "")
	{
		$(".cls_error").show();
		$("#msj_notificacion").text("Debe indicar la sucursal a la que pertenece el usuario.");
		$("#fondo_preloader").hide();
		return false;	
	}

	if($("#id_perfil").val() == "")
	{
		$(".cls_error").show();
		$("#msj_notificacion").text("Debe indicar el perfil del usuario.");
		$("#fondo_preloader").hide();
		return false;	
	}

	if(is_edicion == "0")
	{
		fn_guarda_usuario();	
	}
	else
	{
		fn_edita_usuario()
	}

	

}
function fn_reinicia_psw()
{
	$("#fondo_preloader").show();
	var paramdata = {};
	paramdata["user_name"] = $("#id_username").val();
	paramdata["id_usuario_alta"] = id_usuario_alta;
	var datajson=JSON.stringify(paramdata);

	$.ajax(
		{
			type : "PUT",
			url : ip_local+"/api_reinicia_psw/",
			data : datajson,
			contentType: "application/json; charset=utf-8",
			datatype : "json",
			headers : {
				'X-CSRFToken': csrf_token
			},
			success : function(data)
			{

				data = JSON.parse(data);

				if(data[0].estatus == "0")
				{
					$(".cls_error").show();
					$("#msj_notificacion").text(data[0].msj);
					$("#fondo_preloader").hide();
				}
				else
				{

					$(".cls_exito").show();
					$("#msj_aviso").text(data[0].msj);
					$("#fondo_preloader").hide();	
				}
				$(".cls_confirma_reinicio_psw").hide();
				$("#fondo_preloader").hide();

			},
			error : function(err)
			{
					$(".cls_error").show();
					$("#msj_notificacion").text("Error al reiniciar la contraseña.");
					$(".cls_confirma_reinicio_psw").hide();
					$("#fondo_preloader").hide();
			},
			failure : function (f)
			{
					$(".cls_error").show();
					$("#msj_notificacion").text("Error al reiniciar la contraseña.");
					$(".cls_confirma_reinicio_psw").hide();
					$("#fondo_preloader").hide();
			}

		}
	);
}
function fn_edita_usuario()
{
	$("#fondo_preloader").show();
	var paramdata = {};
	paramdata["id_sucursal"] = $("#id_sucursal").val();
	paramdata["id_perfil"] = $("#id_perfil").val()
	paramdata["user_name"] = $("#id_username").val();
	paramdata["first_name"] = $("#id_first_name").val();
	paramdata["last_name"] = $("#id_last_name").val() ;
	paramdata["id_usuario_alta"] = id_usuario_alta;

	if($("#id_activo").prop("checked"))
	{
		paramdata["activo"] = 1;
	}
	else
	{
		paramdata["activo"] = 0;
	}

	var datajson=JSON.stringify(paramdata);

	$.ajax(
		{
			type : "PUT",
			url : ip_local+"/api_usuario/",
			data : datajson,
			contentType: "application/json; charset=utf-8",
			datatype : "json",
			headers : {
				'X-CSRFToken': csrf_token
			},
			success : function(data)
			{

				data = JSON.parse(data);

				if(data[0].estatus == "0")
				{
					$(".cls_error").show();
					$("#msj_notificacion").text(data[0].msj);
					$("#fondo_preloader").hide();
						
				}
				else
				{

					$(".cls_exito").show();
					$("#msj_aviso").text(data[0].msj);
					$("#fondo_preloader").hide();
						

						
				}
				$("#fondo_preloader").hide();

			},
			error : function(err)
			{
					$(".cls_error").show();
					$("#msj_notificacion").text("Error al editar el usuario.");
					$("#fondo_preloader").hide();
			},
			failure : function (f)
			{
					$(".cls_error").show();
					$("#msj_notificacion").text("Error al editar el usuario.");
					$("#fondo_preloader").hide();
			}

		}
	);
}
function fn_guarda_usuario()
{
	$("#fondo_preloader").show();
	var paramdata = {};
	paramdata["id_sucursal"] = $("#id_sucursal").val();
	paramdata["id_perfil"] = $("#id_perfil").val()
	paramdata["user_name"] = $("#id_username").val();
	paramdata["first_name"] = $("#id_first_name").val();
	paramdata["last_name"] = $("#id_last_name").val() ;
	paramdata["id_usuario_alta"] = id_usuario_alta;
	var datajson=JSON.stringify(paramdata);
	$.ajax(
		{
			type : "POST",
			url : ip_local+"/api_usuario/",
			data : datajson,
			contentType: "application/json; charset=utf-8",
			datatype : "json",
			headers : {
				'X-CSRFToken': csrf_token
			},
			success : function(data)
			{

				data = JSON.parse(data);

				if(data[0].estatus == "0")
				{
					$(".cls_error").show();
					$("#msj_notificacion").text(data[0].msj);
					$("#fondo_preloader").hide();
						
				}
				else
				{

					$(".cls_exito").show();
					$("#msj_aviso").text(data[0].msj);
					$("#fondo_preloader").hide();
						

						
				}
				$("#fondo_preloader").hide();

			},
			error : function(err)
			{
					$(".cls_error").show();
					$("#msj_notificacion").text("Error al registrar el usuario.");
					$("#fondo_preloader").hide();
			},
			failure : function (f)
			{
					$(".cls_error").show();
					$("#msj_notificacion").text("Error al registrar el usuario.");
					$("#fondo_preloader").hide();
			}

		}
	);

}
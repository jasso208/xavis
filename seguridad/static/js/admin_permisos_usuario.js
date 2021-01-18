var id_usuario_a_modificar;
var id_usuario_modifica;
var ip_local;
var csrf_token;
$(document).ready(
		function()
		{
			$("#btn_aceptar_error").click(
					function()
					{
						$(".cls_error").hide();
					}
				);
			$("#btn_consultar").click(
					function()
					{
						fn_consulta_usuario();
					}
				);
			$("#btn_aceptar_exito").click(
				function()
				{

					$(".cls_exito").hide();

				});
		}
	);


function fn_inicio(id_usr_mod,token,ip)
{
	id_usuario_modifica = id_usr_mod;
	csrf_token = token;
	ip_local = ip;

	$("#fondo_preloader").hide();
	$(".cls_error").hide();
	$(".cls_exito").hide();
	id_usuario_a_modificar = 0;

	
	
}

function fn_consulta_usuario()
{
	$(".cls-chbx").prop("checked",false);
	$("#fondo_preloader").show();
	$.ajax(
		{
			type : "GET",
			url: ip_local+"/api_consulta_usuario/",
			data: {"username": $("#txt_nombre_de_usuario").val()},
			contentType : "application/json; charset=utf-8",
			datatype : "json",
			success: function(data)
			{
				var resp = JSON.parse(data);
				
				if(resp[0].estatus == 0)
				{
					$(".cls_error").show();
					$("#msj_notificacion").text(resp[0].msj);
					$("#fondo_preloader").hide();
					$("#span_usuario").text("")
					id_usuario_a_modificar = 0;
					return false
				}
				else
				{
					if (resp[0].nombre_usuario == " ")
					{
						$("#span_usuario").text("Usuario sin nombre registrado")	;
					}
					else
					{
						$("#span_usuario").text(resp[0].nombre_usuario)	;	
					}
					
					id_usuario_a_modificar = resp[0].id_usuario_a_modificar;
					
					for(id_p in resp[1])
					{
						

						if (resp[1][id_p].toString().length == 1)
						{
							

							$("#cbx_00"+resp[1][id_p].toString()).prop("checked",true);
						}
						if  (resp[1][id_p].toString().length == 2)
						{
							$("#cbx_0"+resp[1][id_p].toString()).prop("checked",true);
						}
						if  (resp[1][id_p].toString().length == 3)
						{
							$("#cbx_"+resp[1][id_p].toString()).prop("checked",true);
						}

						
						
					}
				}
				

				

				$("#fondo_preloader").hide();

			},
			error: function(err)
			{

			
					$(".cls_error").show();
					$("#msj_notificacion").text("Error al consultar el usuario.");
					$("#fondo_preloader").hide();
					$("#span_usuario").text("")
					id_usuario_a_modificar = 0;
			},
			failure : function(f)
			{
					$(".cls_error").show();
					$("#msj_notificacion").text("Error al consultar el usuario.");
					$("#fondo_preloader").hide();
					$("#span_usuario").text("")
					id_usuario_a_modificar = 0;
			}


		}
	);
}
function fn_cambia_estatus_permiso(chbx,id)
{
		if (id_usuario_a_modificar == 0)
	{
		$(".cls_error").show();
		$("#msj_notificacion").text("Debe indicar el usuario al que le modificara los permisos.");
		$("#fondo_preloader").hide();

		chbx.checked = !chbx.checked;
		return false;
	}

	$("#fondo_preloader").show();

	metodo = ""
	//damos permiso
	if (chbx.checked)
	{
			var paramdata = {};	
			paramdata["id_usuario"] = id_usuario_a_modificar;
			paramdata["id_item_menu"] = id;
			paramdata["id_usuario_asigna"] = id_usuario_modifica;
			metodo = "POST";
			
	}
	else //Quitamos permiso
	{
			var paramdata = {};	
			paramdata["id_usuario"] = id_usuario_a_modificar;
			paramdata["id_item_menu"] = id;

			metodo = "PUT";
			
	}
	var datajson=JSON.stringify(paramdata);


	$.ajax(
		{
			type : metodo,
			url : ip_local+"/api_permisos_usuario/",
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

					chbx.checked = !chbx.checked;
						
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
					$("#msj_notificacion").text("Error al actualizar los permisos.");
					$("#fondo_preloader").hide();
					chbx.checked = !chbx.checked;
			},
			failure : function (f)
			{
					$(".cls_error").show();
					$("#msj_notificacion").text("Error al actualizar los permisos.");
					$("#fondo_preloader").hide();
					chbx.checked = !chbx.checked;
			}

		}
	);
}

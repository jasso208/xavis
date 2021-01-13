
$(document).ready(
	function()
	{
		fn_inicio();
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
	}
	);

function fn_inicio(is_edicion)
{
	if(is_edicion == "0")
	{
		$("#id_username").val("");
		$("#id_password").show();	

	}
	else
	{
		$("#id_password").hide();		
	}
	$("#id_password").val("12345");	
	$("#id_username").prop("required",false);	
	$(".help-block").hide();
	$(".cls_error").hide();
	
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
		if($("#id_password").val() == "")
	{
		$(".cls_error").show();
		$("#msj_notificacion").text("La contraseña es requerida.");
		$("#fondo_preloader").hide();
		return false;
	}


	return true

}

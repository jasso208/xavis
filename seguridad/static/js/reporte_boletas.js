$(document).ready(
	function()
	{
		

		fn_inicio();
		//####################################################################
		$("#btn_buscar").click(
				function()
				{
					return fn_valida_formulario();
				}
			);

		$("#btn_aceptar_error").click(
				function()
				{
					$(".cls_mensaje_error").hide();					
				}
			);

	}
);

function fn_inicio()
{
	$(".cls_mensaje_error").hide();
	$("#id_estatus").removeAttr("required");
}
function fn_valida_formulario()
{
	if ($("#id_sucursal").val() == "")
	{
		$("#msj_error").text("Debe seleccionar una sucursal.");
		$(".cls_mensaje_error").show();

		return false;
	}
	return true;
}
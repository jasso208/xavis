$(document).ready(
		function()
		{
			fn_inicio();

			$("#id_porcentaje").change(
					function()
					{
						if($("#id_porcentaje").val() == "")
						{
							$("#id_porcentaje").val("0")	

						}


					}
				);
			$("#btn_guardar").click(
					function()
					{
						if(parseFloat($("#id_porcentaje").val()) > 100)
						{
							$("#msj_error").text("El porcentaje indicado no puede ser mayor a 100");
							$(".cls_msj_error").show();												
							return false;
						}

						if(parseFloat($("#id_porcentaje").val()) < 0)
						{
							$("#msj_error").text("El porcentaje indicado no puede ser menor a 0");
							$(".cls_msj_error").show();												
							return false;
						}
						$("#fondo_preloader").show();

						return true
					}
				);
			$("#btn_aceptar_error").click(
					function()
					{

						$(".cls_msj_error").hide();					
					}
				);
			$("#btn_aceptar_error_2").click(
					function()
					{
						$(".cls_error_2").hide();						
					}
				);
		}
	);

function fn_inicio(valor)
{
	$("#id_porcentaje").val(valor);
	$(".cls_msj_error").hide();
	$("#fondo_preloader").hide();
}
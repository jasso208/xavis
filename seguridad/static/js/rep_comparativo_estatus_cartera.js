var fecha_1;
var fecha_2;
var id_sucursal;
$(document).ready(
	function()
	{
	

		$("#btn_aceptar_error_2").click(
				function()
				{
					$(".cls_error_2").hide();					
				}
			);

		$("#btn_aceptar_error_3").click(
				function()
				{
					$(".cls_error_3").hide();
				}
			);
		$("#btn_consultar").click(
			function()
			{
				return fn_valida_formulario_busqueda();
			}
		);
		$("#btn_export_pdf").click(
			function()
			{
				$("#id_export_pdf").val("1");
			}
		);
	
	}
);


function fn_inicio(fec_1,fec_2,id_suc)
{

	fecha_1 = fec_1;
	fecha_2 = fec_2;
	id_sucursal = id_suc;

	$("#id_fecha_inicial").val(fecha_1);
	$("#id_fecha_final").val(fecha_2);
	$("#id_sucursal").val(id_sucursal)

	$("#fondo_preloader").hide();
	$(".cls_error_3").hide();

}

function fn_valida_formulario_busqueda()
{
	$("#fondo_preloader").show();
	if ($("#id_fecha_inicial").val() == "")
	{
		$("#fondo_preloader").hide();
		$(".cls_error_3").show();
		$("#msj_notificacion").text("Debe indicar la primera fecha a comparar.");
		return false;
	}
		if ($("#id_fecha_final").val() == "")
	{
		$("#fondo_preloader").hide();
		$(".cls_error_3").show();
		$("#msj_notificacion").text("Debe indicar la segunda fecha a comparar.");
		return false;
	}


	return true;

}

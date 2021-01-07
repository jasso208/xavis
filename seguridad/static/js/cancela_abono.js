var csrf_token;
var ip_local;
$(document).ready(function()
		{
				$("#btn_aceptar_error").click(
						function()
						{

							$(".cls_mensaje_error").hide();
						}
					);

		}
	)
function fn_inicio(p_csrf_token,ip_l)
{
	csrf_token = p_csrf_token;
	ip_local = ip_l;

	$(".cls_mensaje_error").hide();
	$(".cls_msj_exito").hide();
}

function fn_cancela_abono(id)
{
	$("#fondo_preloader").show();			
			var paramdata = {};
			paramdata["id_abono"] = id;
			
			var datajson=JSON.stringify(paramdata);

			$.ajax(
					{
						type : "PUT",
						url : ip_local+"/empenos/api_cancela_abono/",
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
								$(".cls_mensaje_error").show();
								$("#msj_error").text(data[0].msj);								
							}
							else
							{
									/*url =$("#imprime_abono").attr("href");
		      						window.open(url, '_blank');	
									
									*/
									$(".cls_msj_exito").show();
							}
							$("#fondo_preloader").hide();

						},
						error : function(err)
						{
							$(".cls_mensaje_error").show();
							$("#msj_error").text("Error al cancelar el abono.");
							$("#fondo_preloader").hide();
						},
						failure : function (f)
						{
							$(".cls_mensaje_error").show();
							$("#msj_error").text("Error al cancelar el abono.");
							$("#fondo_preloader").hide();
						}

					}
				);
}
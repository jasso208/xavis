var csrf_token="";
var username="";
var id_boleta="";
var ip_local="";
$(document).ready(
	function()
	{
		


		$("#btn_ayuda").click(
				function()
				{
					$(".cls_ayuda").show();					
				}
			);
		$("#btn_aceptar_ayuda").click(
			function()
			{
				$(".cls_ayuda").hide();				
			}
		);
		$("#btn_no_cancelar").click(
				function()
				{
					$(".cls_confirmacion_baja").hide();
				}
			);

		$("#btn_continuar_cancelacion").click(
				function()
				{
					$(".cls_confirmacion_baja").hide();
					fn_cancela_boleta();
				}
		);
		$("#btn_aceptar_aviso").click(
				function()
				{
					$(".cls_exito").hide();
				}
			);
	}
);

function fn_inicio(token,un,ip)
{

	csrf_token = token;
	username = un;
	ip_local = ip;

	$(".cls_ayuda").hide();
	$(".cls_confirmacion_baja").hide();
	$(".cls_error").hide();
	$("#fondo_preloader").hide();
	$(".cls_exito").hide();

}

function fn_confirma_cancela_boleta(id_b)
{
	id_boleta = id_b;

	$(".cls_confirmacion_baja").show();
}

		function fn_cancela_boleta()
		{
			$("#fondo_preloader").show();
			var dataVal = {};

			dataVal["id_boleta"] = id_boleta;
        	dataVal["username"] = username;      	        	

        	var forminput = JSON.stringify(dataVal);

			$.ajax(
					{
							type : 'DELETE',
							url : ip_local + "/empenos/api_boleta_empeno/",
							data : forminput,
							contentType: "application/json; charset=utf-8",
							datatype : "json",							
						 	headers: {
						       'X-CSRFToken': csrf_token
						   	},
							success : function(data)
							{												
								if (data[0].estatus == "0")
								{
									$("#msj_error").text("Error al cancelar la boleta");
									$(".cls_error").hide();
									
								}
								else
								{
									$("#msj_aviso").text("La boleta se cancelo correctamente.");
									$(".cls_exito").show();

								}

								$("#fondo_preloader").hide();

							},
							error : function(err)
							{

								$("#msj_error").text("Error al cancelar la boleta");
								$(".cls_error").hide();
								$("#fondo_preloader").hide();
							},
							failure : function(f)
							{
								$("#msj_error").text("Error al cancelar la boleta");
								$(".cls_error").hide();
								$("#fondo_preloader").hide();
							}
			
					}


				);
		}
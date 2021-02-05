var csrf_token;
var iplocal ;
var id_usuario;
$(document).ready(
		function()
		{
			fn_inicio();

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
			$("#id_folio").change(
					function()
					{
						fn_consulta_precio_venta();
					}
				);
			$("#id_sucursal").change(
					function ()
					{
						$("#id_folio").val("");
						$("#id_precio_venta").val("");
					}
				);
			$("#btn_aceptar_error_api").click(
				function()
				{
					$(".cls_error_api").hide();
				}
			);
			$("#btn_guardar").click(
					function()
					{
						fn_establece_precio_venta();
					}
				);
			$("#btn_aceptar_exito").click(
					function()
					{

						$(".cls_exito_actualiacion").hide();
					}
				);
		}
	);

function fn_inicio(token,ip,id_usr)
{
	csrf_token = token;
	iplocal = ip;
	id_usuario = id_usr;

	$(".cls_ayuda").hide();
	$("#fondo_preloader").hide();
	$(".cls_error_api").hide();
	$(".cls_exito_actualiacion").hide();
}

function fn_consulta_precio_venta()
			{

				$("#id_precio_venta").val("");

				
				$("#fondo_preloader").show();
				$.ajax({
					type: "GET",
			        url: iplocal + "/empenos/api_precio_venta_fijo/",
			        data: {	
			        			"id_sucursal" : $("#id_sucursal").val(),
			        			"folio_boleta" : $("#id_folio").val()
			    			},
			        contentType: "application/json; charset=utf-8",
			        dataType: "json",
			        success: function (r) {

			        	var resp  = JSON.parse(r);

		    			if (resp[0].estatus == "0")
			        	{
			        		
								$(".cls_error_api").show();		
								$("#msj_error_api").text(resp[0].msj);
								$("#fondo_preloader").hide();
			        	}
			        	else
			        	{	        		
							$("#id_precio_venta").val(resp[0].importe);
			        	}    	
			        	$("#fondo_preloader").hide();
			        },
			        error: function (r) {
			        		
								$(".cls_error_api").show();		
								$("#msj_error_api").text("Error al consultar el precio de venta.");
								$("#fondo_preloader").hide();
			        },
			        failure: function (r) {
			        		
								$(".cls_error_api").show();		
								$("#msj_error_api").text("Error al consultar el precio de venta.");
								$("#fondo_preloader").hide();
			        }
				});

			}
function fn_establece_precio_venta()
			{
				$("#fondo_preloader").show();
				var paramdata = {};

				paramdata["id_sucursal"] = $("#id_sucursal").val();
				paramdata["folio_boleta"] = $("#id_folio").val();
				paramdata["importe"] = $("#id_precio_venta").val();
				paramdata["id_usuario"] = id_usuario;
				

				var datajson=JSON.stringify(paramdata);

				$.ajax(
					{
						type : "PUT",
						url : iplocal+"/empenos/api_precio_venta_fijo/",
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
								$(".cls_error_api").show();		
								$("#msj_error_api").text(data[0].msj);
								$("#fondo_preloader").hide();
							}
							else
							{

								$(".cls_exito_actualiacion").show();
							}
							
							$("#fondo_preloader").hide();

						},
						error : function(err)
						{
								$(".cls_error_api").show();		
								$("#msj_error_api").text("Error al actualizar la información");
								$("#fondo_preloader").hide();
						},
						failure : function (f)
						{
								$(".cls_error_api").show();		
								$("#msj_error_api").text("Error al actualizar la información");
								$("#fondo_preloader").hide();
						}

					}
				);

			}

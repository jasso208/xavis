var min_semanas_refrendar;
var max_semanas_refrendar;
var importe_refrendo;
var importe_compg;
var num_dias_vencido;
var descuento;
var id_boleta;
var ip_local;
var mutuo_boleta;
var csrf_token;
var id_caja;
var total_pagar;
var cambio;
$(document).ready(
		function ()
		{

					$("#int_semanas_a_refrendar").change(
							function()
							{
								fn_valida_semanas_a_refrendar();
							}
						);

					$("#btn_aceptar_error").click(
							function()
							{
								$(".cls_mensaje_error").hide();

							}
						);
					$("#int_abono_capital").change(
							function()
							{
								fn_valida_abono_capital();
								fn_valida_semanas_a_refrendar();	
							}
						);

					$("#btn_simulacion").click(
							function()
							{
								fn_simula_refrendo();
								

							}
						);

					$("#div_fondo_form_simulacion").click(
							function()
							{
								$(".cls_form_simulacion").hide();	
							}
						);

					$("#btn_continuar_simulacion").click(
							function()
							{
								$(".cls_form_simulacion").hide();	
							}
						);

					$("#btn_refrendar").click(
							function()
							{
								fn_aplica_refrendo();
							}
						);
					$("#int_importe_recibi").change(
							function ()
							{
								fn_calcula_cambio();
							}
						);



		}
	);

/*esta funcion la usaremos como constructor*/
function fn_inicio(min_sr,max_sr,imp_ref,imp_compg,num_dias_venc,id_b,ip_l,imp_mutuo,token,id_usr,idcaja)
{

	min_semanas_refrendar = parseInt(min_sr);
	max_semanas_refrendar = parseInt(max_sr);	
	importe_refrendo = parseInt(imp_ref)	
	importe_compg = parseInt(imp_compg);
	num_dias_vencido = parseInt(num_dias_venc);
	id_boleta = parseInt(id_b);
	ip_local = ip_l;
	mutuo_boleta = parseInt(imp_mutuo)
	csrf_token = token;
	id_usuario = id_usr;
	descuento = 0;
	id_caja = idcaja;
	total_pagar = 0;
	$(".cls_mensaje_error").hide();
	$(".cls_form_simulacion").hide();
	$("#fondo_preloader").hide();

	//inicializamos formulario
	$("#int_semanas_a_refrendar").val(max_semanas_refrendar);
	$("#int_abono_capital").val("0");
	$(".cls_msj_exito").hide();
	//funciones de loading
	fn_ingreso_semanas_a_pagar();


}

function fn_calcula_cambio()
{
	if ($("#int_importe_recibi").val() == "")
	{
		$("#int_importe_recibi").val("0")	;
	}
	var  importe_recibi = parseInt($("#int_importe_recibi").val());

	 cambio = importe_recibi - total_pagar;
	$("#lbl_cambio").text("$"+parseFloat(cambio).toFixed(2).toString());

}
function fn_valida_abono_capital()
{
	$("#int_abono_capital").val(parseInt($("#int_abono_capital").val()))
	
	if( parseInt($("#int_abono_capital").val()) < 0 || parseInt($("#int_abono_capital").val()) > mutuo_boleta)
	{
		$(".cls_mensaje_error").show();
		$("#msj_error").text("El abono a capital es incorrecto. Debe ser mayor a 0 y menor a "+ mutuo_boleta.toString());
		$("#int_abono_capital").val(0);

		return false;
	}

	fn_ingreso_semanas_a_pagar();
}
function fn_valida_semanas_a_refrendar()
{
	if (max_semanas_refrendar > 1)
	{
		if(parseInt($("#int_semanas_a_refrendar").val()) < min_semanas_refrendar || parseInt($("#int_semanas_a_refrendar").val()) >max_semanas_refrendar)
		{

			$(".cls_mensaje_error").show();
			$("#msj_error").text("El numero de semanas a refrendar debe estar entre "+min_semanas_refrendar.toString()+" y "+max_semanas_refrendar.toString()+".");

			$("#int_semanas_a_refrendar").val(max_semanas_refrendar);
		}
	}
	fn_ingreso_semanas_a_pagar();
}

//funcion que se ejecuta cuando se ingresan semanas a pagar.
function fn_ingreso_semanas_a_pagar()
{
	if (max_semanas_refrendar == 0 || max_semanas_refrendar == 1)
	{
		$("#int_abono_capital").prop("disabled",false);
		$("#int_semanas_a_refrendar").prop("disabled",true);
	}
	else
	{

		//si el numero de semanas a refrendar introducido es el mismo que el maximo de semanas a refrendar
		//permite abonar a capital.
		if (parseInt($("#int_semanas_a_refrendar").val()) == max_semanas_refrendar)
		{
			$("#int_abono_capital").prop("disabled",false);			
		}
		else
			

		{
			$("#int_abono_capital").prop("disabled",true);	
			$("#int_abono_capital").val(0);		
		}
		
		//como el max de semanas a refrendar no es 0 o 1 , el campo de texto siempre estara habilitado.		
		$("#int_semanas_a_refrendar").prop("disabled",false);
	}

	//validamos si se aplicara descuento
	if (num_dias_vencido >=1 & num_dias_vencido <= 3)//para que aplique el descuento debe tener maximo tres dias de vencimiento
	{
		//si el numero de semanas a refrendar cubre al menos las semansa vencidas.
		//aplicamos descuento
		if (parseInt($("#int_semanas_a_refrendar").val()) >= (max_semanas_refrendar-1) )	
		{
			descuento = importe_compg;

				//si lo que se va abonar a capital es lo mismo que el total del mutuo, se cobra comision pg
				//asi lo solicito Nallely
				if (parseInt($("#int_abono_capital").val()) == mutuo_boleta)
				{
					descuento = 0;
				}

		}
		else
		{
			descuento = 0;
		}

	}


	subtotal = parseFloat(importe_refrendo * parseInt($("#int_semanas_a_refrendar").val())).toFixed(2);

	abono_capital = parseInt($("#int_abono_capital").val());

	$("#p_descuento").text("$"+parseFloat(descuento).toFixed(2).toString());

	$("#p_subtotal").text("$" + subtotal.toString());

	total_pagar = parseFloat(parseInt(subtotal) + parseInt(importe_compg) - parseInt(descuento) + parseInt(abono_capital)).toFixed(2);
	fn_calcula_cambio();
	$("#p_total_pagar").text("$"+total_pagar.toString());
}

function fn_simula_refrendo()
{
	$("#fondo_preloader").show();
	$.ajax(
		{
			type : "GET",
			url: ip_local+"/empenos/api_simula_proximos_pagos_semanal/",
			data: {"id_boleta": id_boleta,"semanas_a_refrendar":parseInt($("#int_semanas_a_refrendar").val()),"abono_capital":$("#int_abono_capital").val()},
			contentType : "application/json; charset=utf-8",
			datatype : "json",
			success: function(data)
			{
				var resp = JSON.parse(data);
				

				if(resp[0].estatus == 0)
				{
					$(".cls_mensaje_error").show();
					$("#msj_error").text("Error al consultar la simulacion de proximos pagos.");
					return false;
				}

				$("#pago_simulacion_1").text("Pago 1: " + resp[1][0]);
				$("#pago_simulacion_2").text("Pago 2: " + resp[1][1]);
				$("#pago_simulacion_3").text("Pago 3: " + resp[1][2]);
				$("#pago_simulacion_4").text("Pago 4: " + resp[1][3]);


				if (parseInt(resp[2].nuevo_mutuo) != 0)
				{					
					$("#nueva_fecha_vencimiento").text( resp[1][3]);
				}
				else
				{
					$("#nueva_fecha_vencimiento").text("Boleta desempeñada.");	
				}
			
				$("#pago_simulacion_1_pesos").text("Importe: $" + resp[2].refrendo_semanal + ".00");
				$("#pago_simulacion_2_pesos").text("Importe: $" + resp[2].refrendo_semanal + ".00");
				$("#pago_simulacion_3_pesos").text("Importe: $" + resp[2].refrendo_semanal + ".00");
				$("#pago_simulacion_4_pesos").text("Importe: $" + resp[2].refrendo_semanal + ".00");

				$("#lbl_nuevo_mutuo").text("Nuevo mutuo: $" + resp[2].nuevo_mutuo + ".00");


				$(".cls_form_simulacion").show();
				$("#fondo_preloader").hide();

			},
			error: function(err)
			{

				$(".cls_mensaje_error").show();
				$("#msj_error").text("Error al consultar la simulacion de proximos pagos.");
				$("#fondo_preloader").hide();
			},
			failure : function(f)
			{
				$(".cls_mensaje_error").show();
				$("#msj_error").text("Error al consultar la simulacion de proximos pagos.");
				$("#fondo_preloader").hide();
			}


		}
	);
}


function fn_aplica_refrendo()
		{
			

			if (cambio < 0)
			{
				$(".cls_mensaje_error").show();
				$("#msj_error").text("El importe recibido no cubre el refrendo.");
				return false;
			}
			$("#fondo_preloader").show();			
			var paramdata = {};
			paramdata["id_boleta"] = id_boleta;
			paramdata["numero_semanas_a_pagar"] = $("#int_semanas_a_refrendar").val();
			paramdata["comision_pg"] = importe_compg;
			paramdata["descuento_comision_pg"] = descuento;
			paramdata["id_usuario"] = id_usuario;
			paramdata["importe_abono"] = total_pagar;
			paramdata["id_caja"] = id_caja;
			paramdata["importe_capital"] = $("#int_abono_capital").val();
			var datajson=JSON.stringify(paramdata);

			$.ajax(
					{
						type : "POST",
						url : ip_local+"/empenos/api_aplica_refrendo_semanal/",
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
									url =$("#imprime_abono").attr("href");
		      						window.open(url, '_blank');	
									$(".cls_msj_exito").show();
							}
							$("#fondo_preloader").hide();

						},
						error : function(err)
						{
							$(".cls_mensaje_error").show();
							$("#msj_error").text("Error al aplicar el refrendo.");
							$("#fondo_preloader").hide();
						},
						failure : function (f)
						{
							$(".cls_mensaje_error").show();
							$("#msj_error").text("Error al aplicar el refrendo.");
							$("#fondo_preloader").hide();
						}

					}
				);
			
		}
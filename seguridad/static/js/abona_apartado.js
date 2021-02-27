var saldo_restante=0;//no puede abonar menos de esto
	var importe_venta=0;//si abona mas de esto, se le dara cambio
	$(document).ready(
			function()
			{

				$("#id_abono").change(
					function()
					{
						if($("#id_abono").val() == ""  || $("#id_abono").val() == "0")
						{
							$(".cls_div_error").show();
							$("#msj_error").text("El abono debe ser mayor que $1.00.");
							$("#id_abono").val("1");
						}

						abono = parseInt($("#id_abono").val() );

						if (abono > saldo_restante)
						{

							$(".cls_div_error").show();
							$("#msj_error").text("El saldo restante es $" + saldo_restante.toString() + ".00");
							$("#id_abono").val(saldo_restante.toString() );	
						}

						abono = parseInt($("#id_abono").val() );
						$("#id_abono").val(abono.toString());
						fn_calcula_cambio();
					}
				);
				$("#btn_aceptar_error").click(
					function()
					{
						$(".cls_div_error").hide();
					}
					)
				;
				$("#int_pago_con").change(
					function()
					{

						if($("#int_pago_con").val() == ""  || $("#int_pago_con").val() == "0")
						{
							$(".cls_div_error").show();
							$("#msj_error").text("Debe indicar con cuanto pago el cliente para calcular el cambio.");
							$("#int_pago_con").val("0");
						}

						pago_con = parseInt($("#int_pago_con").val() );
						$("#int_pago_con").val(pago_con.toString());

						fn_calcula_cambio();
					}

				);

				$("#btn_guardar").click(
						function()
						{

							$("#fondo_preloader").show();
						}
					);
			}
	);
	function fn_inicio(sr,error)
	{

		if (error == "1")
		{
			window.open('/empenos/imprime_apartado#','popup', 'width=400px,height=600px')
		}
		saldo_restante  = sr;
		$("#fondo_preloader").hide();	
		$(".cls_div_error").hide();
		$("#id_abono").val(saldo_restante);
		$("#int_pago_con").val(saldo_restante);
		
		id_abono = parseInt($("#id_abono").val() );
		$("#id_abono").val(id_abono.toString());

		pago_con = parseInt($("#int_pago_con").val() );
		$("#int_pago_con").val(pago_con.toString());



		fn_calcula_cambio();
	}


function fn_calcula_cambio()
{


		int_abono = $("#id_abono").val();
		
		int_pago_con = $("#int_pago_con").val();

		cambio = parseInt(int_pago_con) - parseInt(int_abono);

		restan = saldo_restante - parseInt(int_abono);

		$("#lbl_cambio").text("$" + cambio.toString() + ".00");
		$("#lbl_restan").text("$" + restan.toString() + ".00");

}

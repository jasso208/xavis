
	$(document).ready(
		function()
		{
			fn_inicio();
			$("#btn_aceptar_error").click(
					function()
					{
						$(".cls_error_form_hover").hide()
					}
				);
			$("#guardar").click(
					function()
					{
								return fn_valida_form();		
					}
				);

			$("#btn_aceptar_ayuda").click(
					function()
					{
						$(".cls_ayuda").hide();
					}
				);
			$("#btn_ayuda").click(
					function()
					{
						$(".cls_ayuda").show();	
					}
				);
			$("#id_a_criterio_cajero").change(
					function()
					{

						fn_habilita_casilla();
					}
				);
			$("#id_porc_min_1_mes").change(
					function()
					{
						if($("#id_porc_min_1_mes").val() == "" || $("#id_porc_min_1_mes").val() == "0")
						{

							$(".cls_error_form_hover").show()
							$("#msj_error").text("El valor mínimo aceptado es 1%.");
							

							$("#id_porc_min_1_mes").val("1")	

						}

						if (parseInt($("#id_porc_min_1_mes").val()) > 99)
						{

							$(".cls_error_form_hover").show()
							$("#msj_error").text("El valor máximo aceptado es 99%.");
							

							$("#id_porc_min_1_mes").val("99")	

						}
						$("#id_porc_min_1_mes").val(parseInt($("#id_porc_min_1_mes").val().toString()));

					}
				);
			$("#id_porc_min_2_mes").change(
					function()
					{
						
						if($("#id_porc_min_2_mes").val() == "" || $("#id_porc_min_2_mes").val() == "0")
						{

							$(".cls_error_form_hover").show()
							$("#msj_error").text("El valor mínimo aceptado es 1%.");
							

							$("#id_porc_min_2_mes").val("1")	

						}

						if (parseInt($("#id_porc_min_2_mes").val()) > 99)
						{

							$(".cls_error_form_hover").show()
							$("#msj_error").text("El valor máximo aceptado es 99%.");
							

							$("#id_porc_min_2_mes").val("99")	

						}						
						$("#id_porc_min_2_mes").val(parseInt($("#id_porc_min_2_mes").val() ).toString()); 
					}
				);
			$("#fondo_msj_ayuda").click(
					function()
					{
						$(".cls_ayuda").hide();
					}
				);
		}
	);

	function fn_valida_form()
	{

		var val_1=$("#id_porc_min_1_mes").val();
		var val_2=$("#id_porc_min_2_mes").val();


		//si no ha capturado inforamcion en el formulario
		if (val_1==""  | val_2=="" | parseFloat(val_1)<0  | parseFloat(val_2)<0 | parseFloat(val_1)>100  | parseFloat(val_2)>100)
		{
			$(".cls_error_form_hover").show()
			$("#msj_error").text("Revise la información capturada e intente nuevamente.");
			return false;
		}

		if (parseFloat(val_1)> parseFloat(val_2))
		{

			$(".cls_error_form_hover").show()
			$("#msj_error").text("El porcentaje para apartar 2 meses no puede se mayor que el procentaje para apartar 1 mes.");
			return false;	
		}
		$("#fondo_preloader").show();	
		return true;

	}
	function fn_inicio()
	{
		$("#fondo_preloader").hide();
		$(".cls_error_form_hover").hide()
		$(".cls_ayuda").hide();
		fn_habilita_casilla();
	}
	function fn_habilita_casilla()
	{
		if ($("#id_a_criterio_cajero").prop("checked"))
						{
							$("#id_porc_min_1_mes").prop("readonly",true);
							$("#id_porc_min_2_mes").prop("readonly",true);
						}
						else
						{
							
							$("#id_porc_min_1_mes").prop("readonly",false);
							$("#id_porc_min_2_mes").prop("readonly",false);
						}
	}

	

		var id_registro="";
		var iplocal ;
		var id_kilataje;
		var csrf_token;

			$(document).ready(
					function()
					{
							fn_inicio();
							$("#btn_no_eliminar,#fondo_confirmacion_baja").click(
								function()
								{
									$(".cls_confirmacion_baja").hide();
								}
							);

						$("#fondo_exito_baja,#btn_exito_baja,#fondo_no_baja,#btn_no_baja").click(
								function()
								{
									
									location.reload();
								}
							);
						$("#btn_aceptar_baja").click(
								function()
								{
										$(".cls_confirmacion_baja").hide();
									fn_elimina_costo();
								}
							);
						$("#btn_guardar_kilataje").click(
								function()
								{
									fondo_agregar_kilataje();
								}
							);

						$("#btn_no_kilataje").click(
								function()
								{
									$(".cls_error_alta").hide();
								}
							);

						$("#fondo_error_alta").click(
								function()
								{
									$(".cls_error_alta").hide();
								}
							);

						$("#btn_agregar_kilataje").click(
								function()
								{
									$("#txt_agregar_kilataje").text("Agregar kilataje");

									$("#txt_kilataje").val("");
									$("#txt_kilataje").prop("disabled",false);
									$("#id_tipo_producto").prop("disabled",false);
									$("#id_tipo_kilataje").prop("disabled",false);
									$("#int_importe").val("");

									$("#btn_editar_kilataje").hide();
									$("#btn_guardar_kilataje").show();
									$(".cls_agregar_kilataje").show();
								}
							);

						$("#div_fondo_agregar_kilataje").click(
								function()
								{
									$(".cls_agregar_kilataje").hide();	
								}
							);
						$("#btn_aceptar_error").click(
								function()
								{
									$(".cls_msj_error").hide();
								}
							);
						$(".cls_msj_error").click(
								function()
								{
									$(".cls_msj_error").hide();	
								}
							);
						$("#btn_editar_kilataje").click(
								function()
								{
									fn_edita_kilataje();
								}
							);
						$("#btn_exito_kilataje_edicion").click(
								function ()
								{
									window.location.reload()
								}
							);
					}
		
				);

			function fn_edita_kilataje()
			{
				if($("#int_importe").val()=="0" | $("#int_importe").val()=="")
				{
					$("#id_error_importe").show();
					$("#error_importe").text("Debe ingresar el avaluo.");
					return false;
						
				}

				$(".cls_agregar_kilataje").hide();
				$("#fondo_preloader").show();
				var paramdata = {};

				paramdata["id_kilataje"] = id_kilataje;
				paramdata["avaluo"] = $("#int_importe").val();

				var datajson=JSON.stringify(paramdata);

				$.ajax(
					{
						type : "PUT",
						url : iplocal+"/empenos/api_kiltajes/",
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
								$(".cls_msj_error").show();		
								$("#msj_error").text("Error al actualizar la información");
								$("#fondo_preloader").hide();
							}
							else
							{

								$(".cls_exito_edicion").show();
							}
							
							$("#fondo_preloader").hide();

						},
						error : function(err)
						{
							$(".cls_msj_error").show();		
							$("#msj_error").text("Error al actualizar la información");
							$("#fondo_preloader").hide();
						},
						failure : function (f)
						{
							$(".cls_msj_error").show();		
							$("#msj_error").text("Error al actualizar la información");
							$("#fondo_preloader").hide();
						}

					}
				);

			}
			function fn_consulta_kilataje(id_k)
			{


				id_kilataje = id_k;
				$("#fondo_preloader").show();
				$.ajax({
					type: "GET",
			        url: iplocal + "/empenos/api_kiltajes/",
			        data: {"id_kilataje":id_kilataje},
			        contentType: "application/json; charset=utf-8",
			        dataType: "json",
			        success: function (r) {

			        	var resp  = JSON.parse(r);

		    			if (resp[0].estatus=="0")
			        	{
			        		
							$(".cls_msj_error").show();		
							$("#msj_error").text("Error al cargar la informacion.");
			        	}
			        	else
			        	{	        		
							$("#txt_agregar_kilataje").text("Editar kilataje");
							$(".cls_agregar_kilataje").show();
							$("#btn_editar_kilataje").show();
							$("#btn_guardar_kilataje").hide();

							$("#txt_kilataje").prop("disabled",true);
							$("#id_tipo_producto").prop("disabled",true);
							$("#id_tipo_kilataje").prop("disabled",true);
							


							$("#txt_kilataje").val(resp[0].desc_kilataje);
							$("#int_importe").val(resp[0].avaluo);
							$("#id_tipo_producto").val(resp[0].tipo_producto);
							$("#id_tipo_kilataje").val(resp[0].tipo_kilataje);
			        		
			        	}    	
			        	$("#fondo_preloader").hide();
			        },
			        error: function (r) {
			        		
							$(".cls_msj_error").show();		
							$("#msj_error").text("Error al cargar la información.");
							$("#fondo_preloader").hide();
			        },
			        failure: function (r) {
			        		
							$(".cls_msj_error").show();		
							$("#msj_error").text("Error al cargar la información.");
							$("#fondo_preloader").hide();
			        }
				});

			}

			function fondo_agregar_kilataje()
			{

				$("#id_error_kilataje").hide();
				$("#id_error_importe").hide();
				$("#id_error_guardar").hide();	

				if($("#txt_kilataje").val()=="")
				{
					$("#id_error_kilataje").show();
					$("#error_kilataje").text("Debe ingresar la descripción de kilataje.");
					return false;
				}
				if($("#int_importe").val()=="0" | $("#int_importe").val()=="")
				{
					$("#id_error_importe").show();
					$("#error_importe").text("Debe ingresar el avaluo.");
					return false;
						
				}
				fn_agregar_kilatake_2();
			}
			function fn_eliminar(id)
			{
				id_registro=id;
				$(".cls_confirmacion_baja").show();	
			}
			function fn_inicio(ip_l,token)
			{

				iplocal = ip_l;
				csrf_token = token;

				$(".cls_exito_edicion").hide();
				$(".cls_confirmacion_baja").hide();
				$(".cls_exito_baja").hide();
				$(".cls_no_baja").hide();
				
				$("#fondo_preloader").hide();
				$("#id_error_kilataje").hide();
				$("#id_error_importe").hide();
				$(".cls_error_alta").hide();		
				$(".cls_exito_alta").hide();		
				$("#id_error_guardar").hide();
						
				$(".cls_agregar_kilataje").hide();
				$(".cls_msj_error").hide();
				
			}
			function fn_elimina_costo()
			{
				
				$("#fondo_preloader").show();
				$.ajax({
					type: "GET",
			        url: iplocal + "/empenos/api_elimina_costo_kilataje/",
			        data: {"id":id_registro},
			        contentType: "application/json; charset=utf-8",
			        dataType: "json",
			        success: function (r) {
		    			if (r[0].estatus=="0")
			        	{
			        		
							$(".cls_no_baja").show();				
			        	}
			        	else
			        	{	        		

			        		$(".cls_exito_baja").show();
			        	}    	
			        	$("#fondo_preloader").hide();
			        },
			        error: function (r) {
			        		$(".cls_no_baja").show();				
							$("#fondo_preloader").hide();
			        },
			        failure: function (r) {
			        		$(".cls_no_baja").show();				
							$("#fondo_preloader").hide();
			        }
				});
				
			}

			function fn_agregar_kilatake_2()
			{
				$("#fondo_preloader").show();
				$.ajax({
					type: "GET",
			        url: iplocal + "/empenos/api_agregar_kilataje/",
			        data: {"desc_kilataje":$("#txt_kilataje").val(),"importe":$("#int_importe").val(),"id_tipo_producto":$("#id_tipo_producto").val(),"id_tipo_kilataje":$("#id_tipo_kilataje").val()},
			        contentType: "application/json; charset=utf-8",
			        dataType: "json",
			        success: function (r) {
		    			if (r[0].estatus=="0")
			        	{
			        		
							$("#id_error_guardar").show();			
			        	}
			        	else
			        	{	        		

			        		location.reload();
			        	}

			        	$("#fondo_preloader").hide();
			        },
			        error: function (r) {
			        		$("#id_error_guardar").show();				
							$("#fondo_preloader").hide();
			        },
			        failure: function (r) {
			        		$("#id_error_guardar").show();				
							$("#fondo_preloader").hide();
			        }
				});
			}


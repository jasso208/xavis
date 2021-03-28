var id_vt=0;
	var int_total_pagar=0;
	ip_local="";
	var intmin_apartado_2_mes=0;
	var intmin_apartado_1_mes=0
	var id_cliente=0;
	var username = "";
	var id_sucursal = 0;
	$(document).ready(
			function()
			{
				
				$("#btn_agregar").click(
						function()
						{
							fn_agrega_producto();
						}
					);
			$("#btn_filtrar_cliente").click(
					function()
					{
						fn_busca_cliente();
					}
				);
				$("#btn_aceptar_error_consulta").click(
						function()
						{
							$(".cls_error_consulta").hide();
						}
					);

				$("#btn_aceptar_error_agregar").click(
						function()
						{
							$(".cls_error_agregar").hide();
						}
					);
				$("#btn_cancelar_eliminar").click(
						function ()
						{
							$(".cls_confirma_eliminar").hide();
						}
					);
				$("#btn_aceptar_eliminar").click(
						function()
						{
							$(".cls_confirma_eliminar").hide();

							fn_aceptar_eliminacion();
						}
					);


				$("#btn_confirmar_venta").click(
						function()				
						{
							if($("#id_nombre_cliente").val() == "")
							{
								$(".cls_error_general").show();
								$("#msj_error_general").text("Debe seleccionar un cliente.");
								return false;
							}
							$("#fondo_preloader").show();
						}
					);
				$("#btn_limpiar").click(
						function()
						{
							fn_limpia_cotizacion();
						}
					);

				$("#btn_cancelar_buscacliente").click(
						function()
						{
							$(".cls_seleccionar_cliente").hide();
						}
						);

				$("#btn_agregar_cliente").click(
						function()
						{
							$(".cls_seleccionar_cliente").show();		
						}
					);
				$("#id_pago_cliente").change(
						function()
						{ 
							if ($("#id_pago_cliente").val()=="")
							{
								$("#id_pago_cliente").val("0");
							}
							//redondeamos el pago del cliente para no aceptar centavos
							$("#id_pago_cliente").val(parseInt($("#id_pago_cliente").val()).toString())

							//si el pago del cliente no es sperior al minimo para apartar
							if (intmin_apartado_1_mes>parseInt($("#id_pago_cliente").val()))
							{
								$(".cls_error_general").show();
								$("#msj_error_general").text("El importe a abonar debe ser mayor a $" + intmin_apartado_1_mes.toString()+".00");
								$("#id_pago_cliente").val( intmin_apartado_1_mes.toString());
							}

							//Si el pago del cliente es mayor  o igual al total a pagar,
							//le notificamos que no puede pagar el 100%, que de ser asi debe ir a la 
							//pantalla de ventas.
							if (int_total_pagar <= parseInt($("#id_pago_cliente").val()))
							{
								$(".cls_error_general").show();
								$("#msj_error_general").text("No puede cubrir el total del costo del producto. Si el cliente desea pagar en su totalidad el producto, vaya a la pantalla de venta piso.");
								$("#id_pago_cliente").val((int_total_pagar-1).toString());
							}



							fn_calcula_cambio();

						}


					);
					$("#id_pago_cliente_2").change(
						function()
						{
							if ($("#id_pago_cliente_2").val()=="")
							{
								
								$(".cls_error_general").show();
								$("#msj_error_general").text("El importe minimo para apartar es $1.00.");
								$("#id_pago_cliente_2").val("1");								

							}
							//redondeamos el pago del cliente para no aceptar centavos
							$("#id_pago_cliente_2").val(parseInt($("#id_pago_cliente_2").val()).toString())



							if (parseInt($("#id_pago_cliente_2").val()) == "0")
							{
								$(".cls_error_general").show();
								$("#msj_error_general").text("El importe minimo para apartar es $1.00.");
								$("#id_pago_cliente_2").val("1");								
							}

							//Si el pago del cliente es mayor  o igual al total a pagar,
							//le notificamos que no puede pagar el 100%, que de ser asi debe ir a la 
							//pantalla de ventas.
							if (int_total_pagar <= parseInt($("#id_pago_cliente_2").val()))
							{
								$(".cls_error_general").show();
								$("#msj_error_general").text("No puede cubrir el total del costo del producto. Si el cliente desea pagar en su totalidad el producto, vaya a la pantalla de venta piso.");
								$("#id_pago_cliente_2").val((int_total_pagar-1).toString());
							}



							fn_calcula_cambio();

						}


					);
				$("#btn_aceptar_error_general").click(
						function()
						{
							$(".cls_error_general").hide();
						}
						);
				$("#id_pago_con").change(
						function()
						{
							if($("#id_pago_con").val() == "")
							{
								$(".cls_error_general").show();
								$("#msj_error_general").text("Para calcular el cambio, es necesario capturar el importe con el que pago el cliente.");
								$("#id_pago_con").val("0");
							}
							fn_calcula_cambio();

						}
					);
					$("#id_pago_con_2").change(
						function()
						{
							if($("#id_pago_con_2").val() == "")
							{
								$(".cls_error_general").show();
								$("#msj_error_general").text("Para calcular el cambio, es necesario capturar el importe con el que pago el cliente.");
								$("#id_pago_con_2").val("0");
							}

							fn_calcula_cambio();

						}
					);
				$("#id_fondo_seleccionar_cliente").click(
						function()
						{
							$(".cls_seleccionar_cliente").hide();
						}
					);
				$("#btn_exito").click(
						function()
						{
							location.reload()
						}
					);
				$("#id_num_meses_apartar").change(
						function()
						{
							if ($("#id_num_meses_apartar").val() == "" || $("#id_num_meses_apartar").val() == "0" )
							{
								$(".cls_error_general").show();
								$("#msj_error_general").text("Un mes es el minimo que puede apartar un producto.");
								$("#id_num_meses_apartar").val("1");
							}
						}
					);
				$("#btn_nuevo_cliente").click(
						function()
						{
							window.open("/empenos/alta_cliente","popup",'width=400px,height=600px')
						}
					);
			}
		);

	function fn_inicio( ip_l,un,id_suc,estatus)
	{

		if (estatus == "1")
		{
			window.open("/empenos/imprime_apartado","popup",'width=400px,height=400px')
			$(".cls_exito").show();
		}
		else

		{
			$(".cls_exito").hide();	
		}

		ip_local = ip_l;
		username = un;
		id_sucursal = id_suc;
		
		$("#fondo_preloader").hide();
		$(".cls_error_consulta").hide();
		$(".cls_error_agregar").hide();
		$(".cls_confirma_eliminar").hide();
		
		$(".cls_seleccionar_cliente").hide();
		$(".cls_error_consulta_cliente").hide();
		$("#id_id_cliente").hide();
		fn_consulta_productos_temporales();
		$(".cls_error_general").hide();
		$("#id_pago_con").val("0");
		$("#id_pago_con_2").val("0");

		$("#id_pago_cliente_2").val("1");
		$("#id_num_meses_apartar").val("1");

		


	}

	function fn_calcula_cambio()
	{
		importe_cambio = parseInt($("#id_pago_con").val()) - parseInt($("#id_pago_cliente").val());

		$("#lbl_cambio").text("$" + importe_cambio.toString() + ".00");


		importe_cambio = parseInt($("#id_pago_con_2").val()) - parseInt($("#id_pago_cliente_2").val());

		$("#lbl_cambio_2").text("$" + importe_cambio.toString() + ".00");

	}
	function fn_busca_cliente()
	{
		$("#tabla_cliente tbody tr").remove();
		$("#fondo_preloader").show();
		$.ajax({
			type: "GET",
	        url: ip_local + "/empenos/api_consulta_cliente/",
	        data: {

				"palabra":$("#id_cliente_nomapp").val()

	        },
	        contentType: "application/json; charset=utf-8",
	        dataType: "json",
	        success: function (r) {
	        	
	        	//fallo
	        	if (r[0].estatus=="0")
	        	{
	        		$("#msj_error").text(r[0].msj);

					$(".cls_msj_error").show();

	        	}
	        	else//todo correcto
	        	{

	        		fn_agregarFila_cliente(r[1].lista);

	        	}

	        	$("#fondo_preloader").hide();
	        },
	        error: function (r) {
	        		$("#msj_error").text("Error al consultar el cliente");
					$(".cls_msj_error").show();
					$("#fondo_preloader").hide();
	        },
	        failure: function (r) {
	        		 $("#msj_error").text("Error al consultar el cliente");
					$(".cls_msj_error").show();
					$("#fondo_preloader").hide();
	        }
		});

	}

	function fn_seleccionar_cliente(id)
	{

		$(".cls_seleccionar_cliente").hide();

		$("#fondo_preloader").show();

		$.ajax(
		{
			type:"GET",
			url: ip_local + "/empenos/api_consulta_cliente_2/",
			data: {"id":id},
			contentType: "application/json; charset=utf-8",
			datatype:"json",
			success: function(r)
			{
				if (r[0].estatus=="0")
				{
					$(".cls_error_consulta_cliente").show();
					$("#msj_error_consulta_cliente").text(r[0].msj);
					$("#fondo_preloader").hide();
					$("#txt_cliente").text("");
					id_cliente=0;
					$("#id_id_cliente").val("0");
				}
				else
				{
					$("#txt_cliente").text(r[0].cliente);
					id_cliente=id;
					$("#id_id_cliente").val(id);
					$("#fondo_preloader").hide();
				}
				
			},
			error: function(r)
			{
				$("#msj_error_consulta_cliente").text("Error al consultar el cliente.");
				$(".cls_error_consulta_cliente").show();
				$("#txt_cliente").text("");
				$("#fondo_preloader").hide();
				$("#id_id_cliente").val("0");
				id_cliente=0;
				fn_consulta_productos_temporales();
			},
			failure:function(r)
			{

				$("#msj_error_consulta_cliente").text("Error al consultar el cliente.");
				$(".cls_error_consulta_cliente").show();
				$("#txt_cliente").text("");
				$("#fondo_preloader").hide();
				$("#id_id_cliente").val("0");
				id_cliente=0;
				fn_consulta_productos_temporales();

			}

		});


	}
			function fn_agregarFila_cliente(obj)
			{
   				var cont=obj.length;

   				for(x=0; x<cont;x++)
   				{
   					var htmlTags = '<tr>'+

				        "<td><a onClick='fn_seleccionar_cliente("+obj[x].id+")' class='btn btn-default btn-sm'><span class='glyphicon glyphicon-ok'></span></a><a href='/empenos/edita_cliente/"+obj[x].id.toString()+"' class='btn btn-default btn-sm' target='_blank'><span class='glyphicon glyphicon-search'></span></a></td>"+

				        '<td>' + obj[x].nombre + '</td>'+
				        '<td>' + obj[x].telefono_fijo + '</td>'+
				        '<td>' + obj[x].telefono_celular + '</td>'+
				      '</tr>';
			  	 	$('#tabla_cliente tbody').append(htmlTags);
   				}

			}
	function fn_consulta_productos_temporales()
	{
		$("#fondo_preloader").show();
		$("#tabla_productos tbody tr").remove();
		$.ajax(
			{
				type:"GET",
				url: ip_local  + "/empenos/api_consulta_prod_temporal_apartado/",
				data: {"username":username},
				contentType: "application/json; charset=utf-8",
				datatype:"json",
				success: function(r)
				{

					if (r[0].estatus=="0")
					{

						$(".cls_error_consulta").show();

					}
					else
					{
						obj=r[1].lista;

						var cont=obj.length;

		   				for(x=0; x<cont;x++)
		   				{

		   					var htmlTags = '<tr>'+

						        "<td onclick='fn_eliminar_producto("+obj[x].id+")' ><a><span <span class='glyphicon glyphicon-remove'></span></a></td>"+

						        "<td style='font-size: 9px;'>" + obj[x].folio + '</td>'+
						        "<td style='font-size: 9px;'>" + obj[x].descripcion + '</td>'+
						        "<td style='font-size: 9px;'>" + obj[x].estatus + '</td>'+
						        "<td style='font-size: 9px;'>" + obj[x].tipo_producto + '</td>'+
						        "<td style='font-size: 9px;text-align:right'>$" + obj[x].mutuo + '</td>'+
						        "<td style='font-size: 9px;text-align:right'>$" + obj[x].avaluo + '</td>'+
						        "<td style='font-size: 9px;text-align:right'>$" + obj[x].total + '</td>'+
						      '</tr>';

					      
					  	 	$('#tabla_productos tbody').append(htmlTags);

		   				}

		   				$("#total_mutuo").text("$"+r[2].total_mutuo);
		   				$("#total_avaluo").text("$"+r[2].total_avaluo);
		   				$("#total_pagar").text("$"+r[2].total_pagar);

		   				$("#txt_min_1_mes").text("$"+r[2].min_apartado_1_mes);
		   				$("#txt_min_2_mes").text("$"+r[2].min_apartado_2_mes);

		   				int_total_pagar=r[2].inttotal_pagar;
		   				intmin_apartado_2_mes=r[2].intmin_apartado_2_mes;
		   				intmin_apartado_1_mes=r[2].intmin_apartado_1_mes;

		   				$("#id_pago_cliente").val( intmin_apartado_1_mes.toString());

					}
					$("#fondo_preloader").hide();
					fn_calcula_cambio();
				},
				error: function(r)
				{
					$(".cls_error_consulta").show();
					$("#fondo_preloader").hide();
				},
				failure:function(r)
				{
					$(".cls_error_consulta").show();
					$("#fondo_preloader").hide();
				}

			});
	}

	function fn_eliminar_producto(id)
	{	
		id_vt=id;
		$(".cls_confirma_eliminar").show();
	}
	function fn_aceptar_eliminacion()
	{

		$("#fondo_preloader").show();

			$.ajax(
			{
				type:"GET",
				url: ip_local + "/empenos/api_elimina_prod_apartado/",
				data: {"id":id_vt},
				contentType: "application/json; charset=utf-8",
				datatype:"json",
				success: function(r)
				{
					if (r[0].estatus=="0")
					{
						$(".cls_error_agregar").show();
						$("#msj_error_agregar").text(r[0].msj);
						$("#fondo_preloader").hide();
					}
					fn_consulta_productos_temporales();
				},
				error: function(r)
				{
					$("#msj_error_agregar").text("Error al eliminar el producto.");
					$(".cls_error_agregar").show();
					$("#fondo_preloader").hide();
					fn_consulta_productos_temporales();
				},
				failure:function(r)
				{

					$("#msj_error_agregar").text("Error al eliminar el producto.");
					$(".cls_error_agregar").show();
					$("#fondo_preloader").hide();
					fn_consulta_productos_temporales();

				}

			});

	}
	function fn_limpia_cotizacion()
	{
		
			$("#fondo_preloader").show();

			$.ajax(
			{
				type:"GET",
				url: ip_local + "/empenos/api_limpia_venta_piso/",
				data: {"username":username},
				contentType: "application/json; charset=utf-8",
				datatype:"json",
				success: function(r)
				{
					if (r[0].estatus=="0")
					{
						$(".cls_error_agregar").show();
						$("#msj_error_agregar").text(r[0].msj);
						$("#fondo_preloader").hide();
					}
					fn_consulta_productos_temporales();
				},
				error: function(r)
				{
					$("#msj_error_agregar").text("Error al limpiar la cotización.");
					$(".cls_error_agregar").show();
					$("#fondo_preloader").hide();
					fn_consulta_productos_temporales();
				},
				failure:function(r)
				{

					$("#msj_error_agregar").text("Error al limpiar la cotización.");
					$(".cls_error_agregar").show();
					$("#fondo_preloader").hide();
					fn_consulta_productos_temporales();

				}

			});

	}
	function fn_agrega_producto()
	{

		$("#fondo_preloader").show();

		$.ajax(
			{
				type:"GET",
				url: ip_local + "/empenos/api_agrega_prod_apartado/",
				data: {"username":username,"id_sucursal":id_sucursal,"folio":$("#int_folio_boleta").val()},
				contentType: "application/json; charset=utf-8",
				datatype:"json",
				success: function(r)
				{
					console.log(r);
					if (r[0].estatus=="0")
					{
						$(".cls_error_agregar").show();
						$("#msj_error_agregar").text(r[0].msj);
						$("#fondo_preloader").hide();
					}
					else
					{
						fn_consulta_productos_temporales();
					}
				},
				error: function(r)
				{
					$("#msj_error_agregar").text("Error al agregar el producto.");
					$(".cls_error_agregar").show();
					$("#fondo_preloader").hide();
				},
				failure:function(r)
				{

					$("#msj_error_agregar").text("Error al agregar el producto.");
					$(".cls_error_agregar").show();
					$("#fondo_preloader").hide();

				}

			});

	}
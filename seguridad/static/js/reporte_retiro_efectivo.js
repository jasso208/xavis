$(document).ready(
	function()
	{
		fn_inicio();
	}
	);

function fn_inicio()
{
	$("#abrir_1").hide();
}

function fn_reimprime_comprobante_retiro(id)
{
	link = $("#abrir_1").attr("href");
	
	window.open("/empenos/imprime_comprobante_retiro/"+id.toString()+"/",'popup', 'width=400px,height=400px')
	$(".cls_exito").show();
}
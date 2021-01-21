function fn_reimprime_comprobante_ingreso(id)
{
	link = $("#abrir_1").attr("href");
	
	window.open("/empenos/imprime_comprobante_ingreso/"+id.toString()+"/",'popup', 'width=400px,height=400px')
	$(".cls_exito").show();
}
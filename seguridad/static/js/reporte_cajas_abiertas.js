function fn_reimprime_comprobante_corte_caja(id)
{
	link = $("#abrir_1").attr("href");
	
	window.open("/empenos/imprime_corte_caja/"+id.toString()+"/",'popup', 'width=400px,height=600px')
	$(".cls_exito").show();
}
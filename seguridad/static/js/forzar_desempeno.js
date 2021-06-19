 $(document).ready(
    function(){
        $(".cls_ayuda").hide();

        $("#btn_ayuda").click(
            function(){
                $(".cls_ayuda").show();
            }
        );

        $("#btn_aceptar_ayuda").click(
            function(){                
                $(".cls_ayuda").hide();
            }
        );

        $(".cls_msj_aviso").hide();
        
        $("#btn_aceptar_aviso").click(
            function(){
                $(".cls_msj_aviso").hide();
            }
        );
        $("#btn_guardar").click(
            function(){
                forzarImporteDesempeno()
            }
        );
    }
);

function forzarImporteDesempeno(){
    if($("#id_sucursal").val() == "" || $("#id_sucursal").val() == undefined ){
        $(".cls_msj_aviso").show();
        $("#encabezado_aviso").text("Error!!");
        $("#msj_aviso").text("Debe indicar una sucursal.");
        return false;
    }

    if($("#id_folio").val() == "" || $("#id_folio").val() == undefined){
        $(".cls_msj_aviso").show();
        $("#encabezado_aviso").text("Error!!");
        $("#msj_aviso").text("Debe indicar un folio de boleta.");
        return false;
    }

    
    if($("#id_precio_desempeno").val() == "" || $("#id_precio_desempeno").val() == undefined || parseInt($("#id_precio_desempeno").val()) <= 0){
        $(".cls_msj_aviso").show();
        $("#encabezado_aviso").text("Error!!");
        $("#msj_aviso").text("El importe para desempeño debe ser mayor a cero.");
        return false;
    }

    
}
from django.db import models
from ventas.models import Venta

class Concepto_Ingreso(models.Model):
    desc_concepto_ingreso=models.CharField(max_length=50,null=False)

    def __str__(self):
        return str(self.id)+' '+self.desc_concepto_ingreso

class Concepto_Gasto(models.Model):
    desc_concepto_gasto=models.CharField(max_length=50,null=False)

    def __str__(self):
        return str(self.id)+' '+self.desc_concepto_gasto

class Movs_Ingreso(models.Model):
    id_concepto_ingreso=models.ForeignKey(Concepto_Ingreso,on_delete=models.PROTECT,null=True)
    descripcion=models.CharField(max_length=100,default="")
    importe=models.DecimalField(max_digits=20,decimal_places=2,null=False,default=0.00)
    id_v=models.ForeignKey(Venta,on_delete=models.PROTECT,null=True)
    fecha=models.DateField(null=False)

class Movs_Gasto(models.Model):
    id_concepto_gasto=models.ForeignKey(Concepto_Gasto,on_delete=models.PROTECT,null=True)
    descripcion=models.CharField(max_length=100,default="")
    importe=models.DecimalField(max_digits=20,decimal_places=2,null=False,default=0.00)
    id_v=models.ForeignKey(Venta,on_delete=models.PROTECT,null=True)
    fecha=models.DateField(null=False)
    

class Aux_Reporte_Gasto_Ingreso(models.Model):
    c1=models.CharField(max_length=100,null=True,default="")
    c2=models.CharField(max_length=100,null=True,default="")
    c3=models.CharField(max_length=100,null=True,default="")
    c4=models.CharField(max_length=100,null=True,default="")
    c5=models.CharField(max_length=100,null=True,default="")




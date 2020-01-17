from django.shortcuts import render
from .forms import Concepto_Ingreso_form,Concepto_Gasto_Form,Movs_Ingreso_Form,Busca_Movs_Ingreso_Form,Movs_Gasto_Form,Busca_Movs_Gasto_Form
from .models import Movs_Ingreso,Concepto_Ingreso,Aux_Reporte_Gasto_Ingreso,Concepto_Gasto,Movs_Gasto
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum
import csv
from django.http import HttpResponse
# Create your views here.


def registro_concepto_ingreso(request,id_concepto=None):
    if not request.user.is_authenticated:	
        return HttpResponseRedirect(reverse('seguridad:login'))
    if request.method=="POST":
        form=Concepto_Ingreso_form(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('seguridad:bienvenidos'))
    else:
        form=Concepto_Ingreso_form()
    return render(request,'contabilidad/concepto_ingreso.html',locals())


def registro_concepto_gasto(request,id_concepto=None):
    if not request.user.is_authenticated:	
        return HttpResponseRedirect(reverse('seguridad:login'))
    if request.method=="POST":
        form=Concepto_Gasto_Form(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('seguridad:bienvenidos'))
    else:
        form=Concepto_Gasto_Form()
    return render(request,'contabilidad/concepto_gasto.html',locals())

def registro_movs_ingreso(request):
    if not request.user.is_authenticated:	
        return HttpResponseRedirect(reverse('seguridad:login'))
    if request.method=="POST":
        form=Movs_Ingreso_Form(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('seguridad:bienvenidos'))
    else:
        form=Movs_Ingreso_Form()
    return render(request,'contabilidad/registro_ingreso.html',locals())

def reporte_ingresos(request):
    if not request.user.is_authenticated:	
        return HttpResponseRedirect(reverse('seguridad:login'))
    if request.method=="POST":
        conceptos=[]        
        fecha_i=request.POST.get("fecha_inicial")
        fecha_f=request.POST.get("fecha_final")
 
        ci=Concepto_Ingreso.objects.all()
        Aux_Reporte_Gasto_Ingreso.objects.all().delete()
        print(ci)
        for x in ci:
            movs=Movs_Ingreso.objects.filter(fecha__range=(fecha_i,fecha_f),id_concepto_ingreso=x)
            total_concepto=Movs_Ingreso.objects.filter(fecha__range=(fecha_i,fecha_f),id_concepto_ingreso=x).aggregate(Sum('importe'))
            if total_concepto["importe__sum"]==None:
                print("El concepto no tiene movimientos")
            else:
                #creamos registro del concepto
                Aux_Reporte_Gasto_Ingreso.objects.create(c1=x.desc_concepto_ingreso,c5=total_concepto["importe__sum"])
                #creamos regisrto del detalle del concepto
                for y in movs:
                    if y.id_v==None:
                        Aux_Reporte_Gasto_Ingreso.objects.create(c2=y.descripcion,c3=y.fecha,c4=0,c5=y.importe)
                    else:
                        Aux_Reporte_Gasto_Ingreso.objects.create(c2=y.descripcion,c3=y.fecha,c4=y.id_v.id,c5=y.importe)
        form=Busca_Movs_Ingreso_Form(request.POST)
        bita=Aux_Reporte_Gasto_Ingreso.objects.all()
    else:
        form=Busca_Movs_Ingreso_Form()
    return render(request,'contabilidad/busca_ingresos.html',locals())

def reporte_gastos(request):
    if not request.user.is_authenticated:	
        return HttpResponseRedirect(reverse('seguridad:login'))
    if request.method=="POST":
        conceptos=[]        
        fecha_i=request.POST.get("fecha_inicial")
        fecha_f=request.POST.get("fecha_final")
    
        ci=Concepto_Gasto.objects.all()
        Aux_Reporte_Gasto_Ingreso.objects.all().delete()
        
        for x in ci:
            movs=Movs_Gasto.objects.filter(fecha__range=(fecha_i,fecha_f),id_concepto_gasto=x)
            total_concepto=Movs_Gasto.objects.filter(fecha__range=(fecha_i,fecha_f),id_concepto_gasto=x).aggregate(Sum('importe'))
            if total_concepto["importe__sum"]==None:
                print("El concepto no tiene movimientos")
            else:
                #creamos registro del concepto
                Aux_Reporte_Gasto_Ingreso.objects.create(c1=x.desc_concepto_gasto,c5=total_concepto["importe__sum"])
                #creamos regisrto del detalle del concepto
                for y in movs:
                    if y.id_v==None:
                        Aux_Reporte_Gasto_Ingreso.objects.create(c2=y.descripcion,c3=y.fecha,c4=0,c5=y.importe)
                    else:
                        Aux_Reporte_Gasto_Ingreso.objects.create(c2=y.descripcion,c3=y.fecha,c4=y.id_v.id,c5=y.importe)
        form=Busca_Movs_Gasto_Form(request.POST)
        bita=Aux_Reporte_Gasto_Ingreso.objects.all()
    else:
        form=Busca_Movs_Gasto_Form()
    return render(request,'contabilidad/busca_gastos.html',locals())



def registro_movs_gasto(request):
    if not request.user.is_authenticated:	
        return HttpResponseRedirect(reverse('seguridad:login'))
    if request.method=="POST":
        form=Movs_Gasto_Form(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('seguridad:bienvenidos'))
    else:
        form=Movs_Gasto_Form()
    return render(request,'contabilidad/registro_gasto.html',locals())

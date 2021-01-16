#no usar modelos en esta pantalla
def fn_fecha_vencimiento_valida(fecha_vencimiento):
	try:
		#si el dia es de azueto, buscamos el siguiente hata encontrar un dia que no sea de azueto.
		dv=Dia_No_Laboral.objects.get(fecha=fecha_vencimiento)

		dia_mas = timedelta(days=1)
		#si la fecha de vencimiento existe en los dias inhabiles, buscamos el siguiente dia para que sea el de vencimiento.
		fecha_vencimiento=datetime.combine(fecha_vencimiento+dia_mas, time.min)

		dv=Dia_No_Laboral.objects.get(fecha=fecha_vencimiento)
		dia_mas = timedelta(days=1)

		#si la fecha de vencimiento existe en los dias inhabiles, buscamos el siguiente dia para que sea el de vencimiento.
		fecha_vencimiento=datetime.combine(fecha_vencimiento+dia_mas, time.min)

		dv=Dia_No_Laboral.objects.get(fecha=fecha_vencimiento)
		dia_mas = timedelta(days=1)

		#si la fecha de vencimiento existe en los dias inhabiles, buscamos el siguiente dia para que sea el de vencimiento.
		fecha_vencimiento=datetime.combine(fecha_vencimiento+dia_mas, time.min)

		dv=Dia_No_Laboral.objects.get(fecha=fecha_vencimiento)
		dia_mas = timedelta(days=1)

		#si la fecha de vencimiento existe en los dias inhabiles, buscamos el siguiente dia para que sea el de vencimiento.
		fecha_vencimiento=datetime.combine(fecha_vencimiento+dia_mas, time.min)

	except Exception as e:
		print(e)
		print("la fecha de vencimiento es valida")
	return  fecha_vencimiento
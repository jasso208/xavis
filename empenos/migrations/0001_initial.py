# Generated by Django 3.1 on 2020-08-06 20:33

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Abono',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.CharField(max_length=7, null=True)),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('importe', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
            ],
        ),
        migrations.CreateModel(
            name='Boleta_Empeno',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.IntegerField()),
                ('avaluo', models.IntegerField()),
                ('mutuo', models.IntegerField()),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('fecha_vencimiento', models.DateTimeField()),
                ('nombre_cotitular', models.CharField(default='NA', max_length=20)),
                ('apellido_p_cotitular', models.CharField(default='NA', max_length=20)),
                ('apellido_m_cotitular', models.CharField(default='NA', max_length=20)),
                ('refrendo', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('mutuo_original', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Costo_Kilataje',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kilataje', models.CharField(max_length=10)),
                ('avaluo', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
            ],
        ),
        migrations.CreateModel(
            name='Estatus_Boleta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estatus', models.CharField(max_length=20)),
                ('nombre_corto', models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Linea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('linea', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marca', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Pagos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_vencimiento', models.DateTimeField()),
                ('almacenaje', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('interes', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('iva', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('importe', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('vencido', models.CharField(default='N', max_length=1)),
                ('pagado', models.CharField(default='N', max_length=1)),
                ('fecha_pago', models.DateTimeField(blank=True, null=True)),
                ('boleta', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.boleta_empeno')),
            ],
        ),
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('perfil', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Periodo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consecutivo', models.IntegerField(default=0)),
                ('fecha_vencimiento', models.DateTimeField()),
                ('importe', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('fecha_pago', models.DateTimeField(blank=True, null=True)),
                ('vencido', models.CharField(default='N', max_length=1)),
                ('pagado', models.CharField(default='N', max_length=1)),
                ('boleta', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.boleta_empeno')),
                ('pago', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.pagos')),
            ],
        ),
        migrations.CreateModel(
            name='Plazo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plazo', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Sucursal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sucursal', models.CharField(max_length=100)),
                ('calle', models.CharField(default='', max_length=50, null=True)),
                ('codigo_postal', models.CharField(default='', max_length=10, null=True)),
                ('numero_interior', models.IntegerField(default=0, null=True)),
                ('numero_exterior', models.IntegerField(default=0, null=True)),
                ('colonia', models.CharField(default='', max_length=50, null=True)),
                ('ciudad', models.CharField(default='', max_length=50, null=True)),
                ('estado', models.CharField(default='', max_length=50, null=True)),
                ('pais', models.CharField(default='', max_length=50, null=True)),
                ('telefono', models.CharField(default='', max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tipo_Movimiento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_movimiento', models.CharField(max_length=50)),
                ('naturaleza', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Tipo_Pago',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_pago', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Tipo_Periodo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_periodo', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Tipo_Producto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_producto', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caja', models.CharField(max_length=1, null=True)),
                ('token', models.IntegerField()),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.sucursal')),
                ('tipo_movimiento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_movimiento')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Sucursales_Regional',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.sucursal')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Sub_Linea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_linea', models.CharField(max_length=100)),
                ('linea', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.linea')),
            ],
        ),
        migrations.CreateModel(
            name='Retiro_Efectivo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.CharField(max_length=7, null=True)),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('importe', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(Decimal('1'))])),
                ('comentario', models.TextField()),
                ('caja', models.CharField(max_length=1, null=True)),
                ('token', models.IntegerField()),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.sucursal')),
                ('tipo_movimiento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_movimiento')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rel_Abono_Periodo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abono', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.abono')),
                ('periodo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.periodo')),
            ],
        ),
        migrations.CreateModel(
            name='Rel_Abono_Pago',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abono', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.abono')),
                ('pago', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.pagos')),
            ],
        ),
        migrations.CreateModel(
            name='Rel_Abono_Capital',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('importe', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('capital_restante', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('abono', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.abono')),
                ('boleta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.boleta_empeno')),
            ],
        ),
        migrations.CreateModel(
            name='Periodo_Temp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consecutivo', models.IntegerField(default=0)),
                ('fecha_vencimiento', models.DateTimeField()),
                ('importe', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('fecha_pago', models.DateTimeField(blank=True, null=True)),
                ('vencido', models.CharField(default='N', max_length=1)),
                ('pagado', models.CharField(default='N', max_length=1)),
                ('boleta', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.boleta_empeno')),
                ('pago', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.pagos')),
                ('tipo_periodo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_periodo')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='periodo',
            name='tipo_periodo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_periodo'),
        ),
        migrations.CreateModel(
            name='Pagos_Temp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_vencimiento', models.DateTimeField()),
                ('almacenaje', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('interes', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('iva', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('importe', models.IntegerField()),
                ('vencido', models.CharField(default='N', max_length=1)),
                ('pagado', models.CharField(default='N', max_length=1)),
                ('fecha_pago', models.DateTimeField(blank=True, null=True)),
                ('boleta', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.boleta_empeno')),
                ('tipo_pago', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_pago')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='pagos',
            name='tipo_pago',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_pago'),
        ),
        migrations.CreateModel(
            name='Otros_Ingresos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.CharField(max_length=7, null=True)),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('importe', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(Decimal('1'))])),
                ('comentario', models.CharField(default='', max_length=200)),
                ('caja', models.CharField(max_length=1, null=True)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.sucursal')),
                ('tipo_movimiento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_movimiento')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='linea',
            name='tipo_producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_producto'),
        ),
        migrations.CreateModel(
            name='Imprimir_Boletas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boleta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.boleta_empeno')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Imprime_Abono',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abono', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.abono')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Empenos_Temporal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
                ('avaluo', models.IntegerField()),
                ('mutuo_sugerido', models.IntegerField()),
                ('mutuo', models.IntegerField()),
                ('linea', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.linea')),
                ('marca', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.marca')),
                ('sub_linea', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.sub_linea')),
                ('tipo_producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Dia_No_Laboral',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField()),
            ],
            options={
                'unique_together': {('fecha',)},
            },
        ),
        migrations.CreateModel(
            name='Det_Boleto_Empeno',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
                ('peso', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=20, null=True)),
                ('avaluo', models.IntegerField()),
                ('mutuo_sugerido', models.IntegerField()),
                ('mutuo', models.IntegerField()),
                ('boleta_empeno', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.boleta_empeno')),
                ('costo_kilataje', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.costo_kilataje')),
                ('linea', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.linea')),
                ('marca', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.marca')),
                ('sub_linea', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.sub_linea')),
                ('tipo_producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_producto')),
            ],
        ),
        migrations.AddField(
            model_name='costo_kilataje',
            name='tipo_producto',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_producto'),
        ),
        migrations.CreateModel(
            name='Control_Folios',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.IntegerField()),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.sucursal')),
                ('tipo_movimiento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_movimiento')),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=20)),
                ('apellido_p', models.CharField(max_length=20)),
                ('apellido_m', models.CharField(default='', max_length=20, null=True)),
                ('genero', models.CharField(choices=[('1', 'HOMBRE'), ('2', 'MUJER')], max_length=30)),
                ('estado_civil', models.CharField(choices=[('1', 'SOLTERO'), ('2', 'CASADO')], max_length=30)),
                ('codigo_postal', models.CharField(default='', max_length=10, null=True)),
                ('calle', models.CharField(default='', max_length=50, null=True)),
                ('numero_interior', models.IntegerField(default=0, null=True)),
                ('numero_exterior', models.IntegerField(default=0, null=True)),
                ('colonia', models.CharField(default='', max_length=50, null=True)),
                ('ciudad', models.CharField(default='', max_length=50, null=True)),
                ('estado', models.CharField(default='', max_length=50, null=True)),
                ('pais', models.CharField(default='', max_length=50, null=True)),
                ('telefono_fijo', models.CharField(default='', max_length=10, null=True)),
                ('telefono_celular', models.CharField(max_length=10)),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cajas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.CharField(max_length=7, null=True)),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('importe', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('caja', models.CharField(max_length=1)),
                ('real_tarjeta', models.IntegerField(default=0)),
                ('real_efectivo', models.IntegerField(default=0)),
                ('teorico_tarjeta', models.IntegerField(default=0)),
                ('teorico_efectivo', models.IntegerField(default=0)),
                ('diferencia', models.IntegerField(default=0)),
                ('fecha_cierre', models.DateTimeField(null=True)),
                ('centavos_10', models.IntegerField(default=0)),
                ('centavos_50', models.IntegerField(default=0)),
                ('pesos_1', models.IntegerField(default=0)),
                ('pesos_2', models.IntegerField(default=0)),
                ('pesos_5', models.IntegerField(default=0)),
                ('pesos_10', models.IntegerField(default=0)),
                ('pesos_20', models.IntegerField(default=0)),
                ('pesos_50', models.IntegerField(default=0)),
                ('pesos_100', models.IntegerField(default=0)),
                ('pesos_200', models.IntegerField(default=0)),
                ('pesos_500', models.IntegerField(default=0)),
                ('pesos_1000', models.IntegerField(default=0)),
                ('token_cierre_caja', models.IntegerField(null=True)),
                ('comentario', models.TextField(default='')),
                ('estatus_guardado', models.IntegerField(default=0)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.sucursal')),
                ('tipo_movimiento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_movimiento')),
                ('user_cierra_caja', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='boleta_empeno',
            name='caja',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.cajas'),
        ),
        migrations.AddField(
            model_name='boleta_empeno',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.cliente'),
        ),
        migrations.AddField(
            model_name='boleta_empeno',
            name='estatus',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='empenos.estatus_boleta'),
        ),
        migrations.AddField(
            model_name='boleta_empeno',
            name='plazo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.plazo'),
        ),
        migrations.AddField(
            model_name='boleta_empeno',
            name='sucursal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.sucursal'),
        ),
        migrations.AddField(
            model_name='boleta_empeno',
            name='tipo_producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_producto'),
        ),
        migrations.AddField(
            model_name='boleta_empeno',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='abono',
            name='boleta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.boleta_empeno'),
        ),
        migrations.AddField(
            model_name='abono',
            name='caja',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.cajas'),
        ),
        migrations.AddField(
            model_name='abono',
            name='sucursal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.sucursal'),
        ),
        migrations.AddField(
            model_name='abono',
            name='tipo_movimiento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='empenos.tipo_movimiento'),
        ),
        migrations.AddField(
            model_name='abono',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='User_2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sesion', models.IntegerField()),
                ('perfil', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.perfil')),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.sucursal')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user',)},
            },
        ),
        migrations.CreateModel(
            name='Joyeria_Empenos_Temporal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('peso', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('costo_kilataje', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.costo_kilataje')),
                ('empeno_temporal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empenos.empenos_temporal')),
            ],
            options={
                'unique_together': {('empeno_temporal',)},
            },
        ),
        migrations.AlterUniqueTogether(
            name='boleta_empeno',
            unique_together={('folio', 'sucursal')},
        ),
    ]

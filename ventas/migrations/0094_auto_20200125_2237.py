# Generated by Django 2.2.6 on 2020-01-26 04:37

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0093_auto_20200125_2229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venta',
            name='fecha',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 26, 4, 37, 29, 569438, tzinfo=utc)),
        ),
    ]

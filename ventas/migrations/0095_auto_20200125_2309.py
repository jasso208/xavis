# Generated by Django 2.2.6 on 2020-01-26 05:09

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0094_auto_20200125_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venta',
            name='fecha',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 26, 5, 9, 24, 482232, tzinfo=utc)),
        ),
    ]

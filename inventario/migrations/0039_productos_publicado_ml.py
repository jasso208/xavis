# Generated by Django 2.2.6 on 2020-01-26 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0038_auto_20200120_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='productos',
            name='publicado_ml',
            field=models.BooleanField(default=False),
        ),
    ]

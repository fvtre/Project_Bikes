# Generated by Django 4.2.13 on 2024-07-09 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_arriendo_fecha_fin'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicio',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='servicio/'),
        ),
    ]

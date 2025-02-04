# Generated by Django 5.1.2 on 2025-01-17 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_producto_color_alter_producto_descripcion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='destacado',
            field=models.BooleanField(default=False, verbose_name=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='producto',
            name='categoria',
            field=models.CharField(choices=[('seguridad', 'Seguridad'), ('casco', 'Casco'), ('guantes', 'Guantes'), ('ropa', 'Ropa'), ('goggles', 'Goggles'), ('otros', 'Otros')], max_length=100),
        ),
    ]

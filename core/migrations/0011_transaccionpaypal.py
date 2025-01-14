# Generated by Django 5.1.4 on 2025-01-14 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_contacto'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransaccionPaypal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payer_id', models.CharField(max_length=250)),
                ('paymetn_date', models.DateTimeField()),
                ('payment_status', models.CharField(max_length=250)),
                ('quantity', models.IntegerField()),
                ('invoice', models.CharField(max_length=250)),
                ('first_name', models.CharField(max_length=250)),
                ('payer_status', models.CharField(max_length=250)),
                ('payer_email', models.CharField(max_length=250)),
                ('txn_id', models.CharField(max_length=250)),
                ('receiver_id', models.CharField(max_length=250)),
                ('payment_gross', models.FloatField()),
                ('custom', models.CharField(max_length=250)),
            ],
        ),
    ]
# Generated by Django 4.2.7 on 2023-11-23 21:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0004_remove_equipmentreservation_equipment_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipmentreservation',
            name='quantity',
        ),
    ]
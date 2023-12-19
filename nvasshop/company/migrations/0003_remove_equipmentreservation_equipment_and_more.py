# Generated by Django 4.2.7 on 2023-11-23 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipmentreservation',
            name='equipment',
        ),
        migrations.AddField(
            model_name='equipmentreservation',
            name='equipment',
            field=models.ManyToManyField(related_name='equipment_reservations', to='company.equipment'),
        ),
    ]

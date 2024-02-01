# Generated by Django 4.2.7 on 2024-02-01 14:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0006_contract_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='version',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pickupschedule',
            name='version',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
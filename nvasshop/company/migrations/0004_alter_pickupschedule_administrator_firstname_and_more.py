# Generated by Django 4.2.7 on 2023-12-14 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0003_remove_pickupschedule_administrator_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pickupschedule',
            name='administrator_firstName',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='pickupschedule',
            name='administrator_lastName',
            field=models.CharField(default='', max_length=30),
        ),
    ]
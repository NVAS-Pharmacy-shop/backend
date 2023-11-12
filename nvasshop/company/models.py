from django.db import models

# Create your models here.


class Company(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    description = models.CharField(max_length=240, default="")
    email = models.CharField(max_length=50)
    website = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)


class Equipment(models.Model):
    company = models.ForeignKey(Company, related_name='equipment', on_delete=models.CASCADE, default=0)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)

class PickupSchedule(models.Model):
    company = models.ForeignKey(Company, related_name='pickup_schedules', on_delete=models.CASCADE, default=0)
    administrator_name = models.CharField(max_length=30)
    date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.IntegerField()


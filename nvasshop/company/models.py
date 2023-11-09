from django.db import models

# Create your models here.


class Company(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    website = models.CharField(max_length=50)


class Equipment(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=50)


class Company_Equipment(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
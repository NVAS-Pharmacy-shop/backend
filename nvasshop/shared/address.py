from django.db import models

class Address(models.Model):
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)
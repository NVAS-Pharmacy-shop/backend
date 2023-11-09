from django.db import models

# Create your models here.


class User(models.Model):
    class Role(models.TextChoices):
        SYSTEM_ADMIN = 'system_admin'
        COMPANY_ADMIN = 'company_admin'
        EMPLOYEE = 'employee'

    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    role = models.CharField(max_length=15, choices=Role.choices)
    penal_amount = models.IntegerField(default=0)
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, null=True, blank=True)

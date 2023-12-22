from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from .managers import CustomUserManager

# Create your models here.


class User(AbstractUser):
    class Role(models.TextChoices):
        SYSTEM_ADMIN = 'system_admin'
        COMPANY_ADMIN = 'company_admin'
        EMPLOYEE = 'employee'

    username = None

    email = models.EmailField(("email address"), unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=15, choices=Role.choices)
    penal_amount = models.IntegerField(default=0)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, null=True, blank=True, related_name='admin')
    first_login = models.BooleanField(default=True)

    REQUIRED_FIELDS = [] #username (email u nasem slucaju) i pw ce svakako uvek biti required
    USERNAME_FIELD = "email"

    objects = CustomUserManager()

    def __str__(self):
        return self.email
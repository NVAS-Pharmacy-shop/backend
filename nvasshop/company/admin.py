from django.contrib import admin

# Register your models here.

from .models import Company, Equipment

admin.site.register(Company)
admin.site.register(Equipment)
from django.contrib import admin

# Register your models here.

from .models import Company, Equipment, EquipmentReservation

admin.site.register(Company)
admin.site.register(Equipment)
admin.site.register(EquipmentReservation)
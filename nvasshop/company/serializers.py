from rest_framework import serializers
from . import models

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Equipment
        fields = ['name', 'description', 'quantity', 'type', 'company']

class PickupScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PickupSchedule
        fields = ['id', 'administrator_name', 'date', 'start_time', 'duration_minutes']

class CompanySerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(many=True, read_only=True)
    class Meta:
        model = models.Company
        fields = ['id', 'name', 'address', 'email', 'website', 'rate', 'equipment', ]

class CompanyBaseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = ['id', 'name', 'address', 'email', 'website', 'rate', 'description' ]

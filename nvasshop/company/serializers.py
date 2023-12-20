from rest_framework import serializers

from user.serializers import UserSerializer, CompanyAdminSerializer
from . import models


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Equipment
        fields = ['id', 'name', 'description', 'quantity', 'type', 'company']


class PickupScheduleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    company_admin = CompanyAdminSerializer(read_only=True)
    class Meta:
        model = models.PickupSchedule
        fields = ['id', 'company', 'user',
                  'date', 'start_time', 'duration_minutes', 'company_admin', 'status']


class CompanySerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(many=True, read_only=True)
    pickup_schedules = PickupScheduleSerializer(many=True, read_only=True)
    class Meta:
        model = models.Company
        fields = ['id', 'name', 'address', 'email', 'website', 'rate', 'description',
                  'equipment', 'pickup_schedules']


class CompanyBaseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = ['id', 'name', 'address', 'email', 'website', 'rate', 'description' ]

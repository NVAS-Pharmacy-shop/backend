from rest_framework import serializers

from user.serializers import UserSerializer, CompanyAdminSerializer
from . import models


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Equipment
        fields = ['id', 'name', 'description', 'quantity', 'type', 'company']


class PickupScheduleSerializer(serializers.ModelSerializer):
    company_admin = CompanyAdminSerializer(read_only=True)
    class Meta:
        model = models.PickupSchedule
        fields = ['id', 'company',
                  'date', 'start_time', 'end_time', 'company_admin']


class FullInfoCompanySerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(many=True, read_only=True)
    filtered_pickup_schedules = PickupScheduleSerializer(many=True, read_only=True)
    class Meta:
        model = models.Company
        fields = ['id', 'name', 'address', 'email', 'website', 'rate', 'description',
                  'equipment', 'filtered_pickup_schedules']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = ['id', 'name', 'address', 'email', 'website', 'rate', 'description']

class CompanyBaseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = ['id', 'name', 'address', 'email', 'website', 'rate', 'description' ]

class ReservationSerializer(serializers.ModelSerializer):
    user_first_name = serializers.CharField(source='user.first_name')
    user_last_name = serializers.CharField(source='user.last_name')
    date = serializers.DateField(source='pickup_schedule.date')
    start_time = serializers.TimeField(source='pickup_schedule.start_time')
    duration_minutes = serializers.TimeField(source='pickup_schedule.duration_minutes')

    class Meta:
        model = models.EquipmentReservation
        fields = ['user_first_name', 'user_last_name', 'date', 'start_time', 'duration_minutes']

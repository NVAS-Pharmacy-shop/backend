from rest_framework import serializers
from . import models
from .models import Contract
from user.models import User


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Equipment
        fields = ['id', 'name', 'description', 'quantity', 'type', 'company', 'reserved_quantity']


class CompanyAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class PickupScheduleSerializer(serializers.ModelSerializer):
    company_admin = CompanyAdminSerializer(read_only=True)
    class Meta:
        model = models.PickupSchedule
        fields = ['id', 'company', 'date', 'start_time', 'end_time', 'company_admin']


class FullInfoCompanySerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(many=True, read_only=True)
    filtered_pickup_schedules = PickupScheduleSerializer(many=True, read_only=True)
    class Meta:
        model = models.Company
        fields = ['id', 'name', 'address', 'email', 'website', 'rate', 'description',
                  'equipment', 'filtered_pickup_schedules']


class CompanySerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(many=True, read_only=True)
    class Meta:
        model = models.Company
        fields = ['id', 'name', 'address', 'email', 'website', 'rate', 'description', 'equipment']


class CompanyBaseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = ['id', 'name', 'address', 'email', 'website', 'rate', 'description' ]


class ReservationSerializer(serializers.ModelSerializer):
    reservation_id = serializers.IntegerField(source = 'id')
    user_first_name = serializers.CharField(source='user.first_name')
    user_last_name = serializers.CharField(source='user.last_name')
    date = serializers.DateField(source='pickup_schedule.date')
    start_time = serializers.TimeField(source='pickup_schedule.start_time')
    end_time = serializers.TimeField(source='pickup_schedule.end_time')

    class Meta:
        model = models.EquipmentReservation
        fields = ['reservation_id', 'user_first_name', 'user_last_name', 'date', 'start_time', 'end_time']



class PickupScheduleCalendarSerializer(serializers.ModelSerializer):
    user_first_name = serializers.SerializerMethodField()
    user_last_name = serializers.SerializerMethodField()
    date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    class Meta:
        model = models.PickupSchedule
        fields = ['user_first_name', 'user_last_name', 'date', 'start_time', 'end_time']

    def get_user_first_name(self, obj):
        return 'Open'

    def get_user_last_name(self, obj):
        return 'appointment'
    

class ContractSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    equipment = EquipmentSerializer(many=True)

    class Meta:
        model = Contract
        fields = ['id', 'hospital', 'date', 'company', 'equipment']

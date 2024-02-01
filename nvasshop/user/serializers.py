from rest_framework import serializers

from company.serializers import ReservationSerializer
from . import models

class UserSerializer(serializers.ModelSerializer):
    user_reservations = ReservationSerializer(many=True, read_only=True)
    class Meta:
        model = models.User
        fields = '__all__'

class CompanyAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'first_name', 'last_name', 'email']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'first_name', 'last_name', 'email']
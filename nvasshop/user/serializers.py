from rest_framework import serializers
from . import models

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'

class CompanyAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['username', 'email', 'first_name', 'last_name']
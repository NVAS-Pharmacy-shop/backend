from rest_framework import serializers
from . import models

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Equipment
        fields = ['name', 'description', 'quantity']
class CompanySerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(many=True, read_only=True)
    class Meta:
        model = models.Company
        fields = ['id', 'name', 'address', 'email', 'website', 'rate', 'equipment']

from rest_framework import serializers
from user.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User 
        fields = ['first_name', 'last_name', 'email', 'password']
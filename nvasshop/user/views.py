from django.shortcuts import render

# Create your views here.

from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from . import models
from . import serializers
from rest_framework.permissions import IsAuthenticated
from auth.custom_permissions import IsSystemAdmin

class User(APIView):



    def get(self, request, id=None):
        print(request.META)
        if id:
            user = models.User.objects.get(id=id)
            serializer = serializers.UserSerializer(user)
            if request.user.is_authenticated:
                print('auth')
            else:
                print('not auth')
            return Response({'msg': 'get user by id', 'user': serializer.data}, status=status.HTTP_200_OK)

        else:
            users = models.User.objects.all()
            serializer = serializers.UserSerializer(users, many=True)
            return Response({'msg': 'get all user', 'user': serializer.data}, status=status.HTTP_200_OK)

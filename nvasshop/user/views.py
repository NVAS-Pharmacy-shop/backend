from django.shortcuts import render

# Create your views here.

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from . import models
from . import serializers

class User(APIView):
    def get(self, request, id=None):
        if id:
            user = models.User.objects.get(id=id)
            serializer = serializers.UserSerializer(user)
            return Response({'msg': 'get user by id', 'user': serializer.data}, status=status.HTTP_200_OK)

        else:
            users = models.User.objects.all()
            serializer = serializers.UserSerializer(users, many=True)
            return Response({'msg': 'get all user', 'user': serializer.data}, status=status.HTTP_200_OK)

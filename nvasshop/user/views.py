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
from django.shortcuts import get_object_or_404
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

    def put(self, request, id=None):
        if not request.user.is_authenticated:
            return Response({'error' : 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.role != models.User.Role.COMPANY_ADMIN:
            return Response({'error': 'Permission denied. Company admin role required.'},
                            status=status.HTTP_403_FORBIDDEN)
        if id:
            user = get_object_or_404(User, id=id)
            serializer = serializers.UserSerializer(user, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': 'Company Admin user profile updated successfully', 'user': serializer.data}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'User ID is required for profile update'}, status=status.HTTP_400_BAD_REQUEST)
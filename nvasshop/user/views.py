from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from . import models
from . import serializers
from rest_framework.permissions import IsAuthenticated
from auth.custom_permissions import IsSystemAdmin
from django.shortcuts import get_object_or_404
from shared.mixins import PermissionPolicyMixin
from auth.custom_permissions import IsCompanyAdmin
from user.models import User


class User(PermissionPolicyMixin, APIView):

    permission_classes_per_method = {
        "get": [IsAuthenticated],
        "put": [IsAuthenticated],
    }
    
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
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        # if request.user.role != models.User.Role.COMPANY_ADMIN:
        #     return Response({'error': 'Permission denied. Company admin role required.'},
        #                     status=status.HTTP_403_FORBIDDEN)
        if id != request.user.id:
            return Response({'error': 'Permission denied. You can only update your own profile.'},
                            status=status.HTTP_403_FORBIDDEN)
        if id:
            try:
                user = models.User.objects.get(id=id)
            except models.User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = serializers.UserSerializer(user, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': 'Company Admin user profile updated successfully', 'user': serializer.data}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'User ID is required for profile update'}, status=status.HTTP_400_BAD_REQUEST)


class CompanyAdmin(PermissionPolicyMixin, APIView):
    permission_classes_per_method = {
        "get": [IsAuthenticated, IsCompanyAdmin],
        "put":  [IsAuthenticated, IsCompanyAdmin]
    }
    def get(self, request, id=None):
        if id:
            users = models.User.objects.filter(company_id=id)
            serializer = serializers.CompanyAdminSerializer(users, many=True)
            return Response({'msg': 'get all user', 'user': serializer.data}, status=status.HTTP_200_OK)
        else:
            users = models.User.objects.filter(company_id=request.user.company.id)
            serializer = serializers.CompanyAdminSerializer(users, many=True)
            return Response({'msg': 'get all user', 'user': serializer.data}, status=status.HTTP_200_OK)
    def put(self, request):
        try:
            user = models.User.objects.get(id=request.user.id)
            serializer = serializers.UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': 'Company Admin user profile updated successfully', 'user': serializer.data},
                                status=status.HTTP_200_OK)
            return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except models.User.DoesNotExist:
            return Http404("Given query not found....")
    
class CompanyAdminCompanyId(PermissionPolicyMixin, APIView):
    permission_classes_per_method = {
        "get": [IsAuthenticated, IsCompanyAdmin],
    }

    def get(self, request):
        return Response({'company_id': request.user.company.id}, status=status.HTTP_200_OK)

class CompanyAdmin_PasswordChange(PermissionPolicyMixin, APIView):
    permission_classes_per_method = {
        "put": [IsAuthenticated]
    }
    def put(self, request):
        try:
            user = models.User.objects.get(email=request.user.email)
            user.set_password(request.data['password'])
            user.first_login = False
            user.save()
            return Response({'msg': 'Company Admin user profile updated successfully'},
                            status=status.HTTP_200_OK)
        except models.User.DoesNotExist:
            return Http404("Given query not found....")


from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from . import models
from . import serializers
from rest_framework.permissions import IsAuthenticated
from auth.custom_permissions import IsCompanyAdmin
from shared.mixins import PermissionPolicyMixin

class Company(PermissionPolicyMixin, APIView):
    permission_classes_per_method = {
        "get": [IsAuthenticated, IsCompanyAdmin],
        "put": [IsAuthenticated, IsCompanyAdmin],
    }

    def get(self, request, id=None):
        if id:
            try:
                company = models.Company.objects.get(id=id)
                serializer = serializers.CompanySerializer(company)
                return Response({'msg': 'get company', 'company': serializer.data}, status=status.HTTP_200_OK)
            except models.Company.DoesNotExist:
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            companies = models.Company.objects.all()
            serializer = serializers.CompanySerializer(companies, many=True)
            return Response({'msg': 'get all companies', 'company': serializer.data}, status=status.HTTP_200_OK)
    def put(self, request, id):
        try:
            company = models.Company.objects.get(id=id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Equipment(APIView):
    def get(self, request):
        filters = {}
        if 'company_id' in request.GET:
            filters['company_id'] = request.GET['company_id']
        if 'name_substring' in request.GET:
            filters['name__icontains'] = request.GET['name_substring']
        if 'type' in request.GET:
            filters['type'] = request.GET['type']
        if 'company_rating' in request.GET:
            filters['company__rate__gte'] = request.GET['company_rating']

        equipment = models.Equipment.objects.filter(**filters)
        serializer = serializers.EquipmentSerializer(equipment, many=True)
        return Response({'msg': 'get matching equipment', 'equipment': serializer.data}, status=status.HTTP_200_OK)
    
class CompanyBaseInfo(APIView):
    def get(self, request, id):
        try:
            company = models.Company.objects.get(id=id)
            serializer = serializers.CompanyBaseInfoSerializer(company)
            return Response({'msg': 'get company', 'company': serializer.data}, status=status.HTTP_200_OK)
        except models.Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
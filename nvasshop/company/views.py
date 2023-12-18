from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from . import models
from . import serializers
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from auth.custom_permissions import IsCompanyAdmin, IsSystemAdmin
from shared.mixins import PermissionPolicyMixin

class Company(PermissionPolicyMixin, APIView):
    permission_classes_per_method = {
        "get": [IsAuthenticated],
        "put": [IsAuthenticated, IsCompanyAdmin]
    }

    def get(self, request, id=None):
        print(request.user.role)
        if (id==None):
            if(request.user.role.__eq__('company_admin')):
                try:
                    company = models.Company.objects.get(id=request.user.company.id)
                    serializer = serializers.CompanySerializer(company)
                    return Response({'msg': 'get company', 'company': serializer.data}, status=status.HTTP_200_OK)
                except models.Company.DoesNotExist:
                    return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
        elif id:
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
    
    def _validate_required_fields(self, data):
        required_fields = ['name', 'address', 'description', 'website', 'email']
        for field in required_fields:
            if field not in data:
                return False, f'{field} is required'
        return True, None

    def post(self, request):
        is_valid, error_message = self._validate_required_fields(request.data)

        if not is_valid:
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'create company', 'company': serializer.data}, status=status.HTTP_201_CREATED)
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
    def get(self, request, id=None):
        if id:
            try:
                company = models.Company.objects.get(id=id)
                serializer = serializers.CompanyBaseInfoSerializer(company)
                return Response({'msg': 'get company', 'company': serializer.data}, status=status.HTTP_200_OK)
            except models.Company.DoesNotExist:
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            companies = models.Company.objects.all()
            serializer = serializers.CompanyBaseInfoSerializer(companies, many=True)
            return Response({'msg': 'get all companies', 'companies': serializer.data}, status=status.HTTP_200_OK)


class PickupSchedule(PermissionPolicyMixin, APIView):
    permission_classes_per_method = {
        "get": [IsAuthenticated],
        "post": [IsAuthenticated, IsCompanyAdmin]
    }
    def post(self, request):
        try:
            data = request.data
            data['company'] = request.user.company.id
            serializer = serializers.PickupScheduleSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                print("serializer data:", serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Equipment_CompanyAdmin(APIView):
    permission_classes_per_method = {
        "get": [IsAuthenticated, IsCompanyAdmin],
        "post": [IsAuthenticated, IsCompanyAdmin],
        "put": [IsAuthenticated, IsCompanyAdmin],
        "delete": [IsAuthenticated, IsCompanyAdmin],
    }

    def get(self, request, id=None):
        if id:
            try:
                equipment = models.Equipment.objects.get(id=id)
                serializer = serializers.EquipmentSerializer(equipment)
                return Response({'msg': 'get equipment', 'equipment': serializer.data}, status=status.HTTP_200_OK)
            except models.Equipment.DoesNotExist:
                return Response({'error': 'Equipment not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            if (request.query_params.get('name', '')):
                try:
                    name = request.query_params.get('name', '')
                    equipments = models.Equipment.objects.all()
                    equipments = equipments.filter(name__icontains=name, company=request.user.company)
                    serializer = serializers.EquipmentSerializer(equipments, many=True)
                    return Response({'msg': 'search equipment', 'equipment': serializer.data},
                                    status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'error': 'Invalid data', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                equipments = models.Equipment.objects.all().filter(company=request.user.company)
                serializer = serializers.EquipmentSerializer(equipments, many=True)
                return Response({'msg': 'get all equipments', 'equipment': serializer.data}, status=status.HTTP_200_OK)

    def put(self, request):
        try:
            print(request.data)
            equipment = models.Equipment.objects.get(id=request.data['id'])
            serializer = serializers.EquipmentSerializer(equipment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': 'Equipment updated successfully', 'equipment': serializer.data},
                                status=status.HTTP_200_OK)
            return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except models.Equipment.DoesNotExist:
            return Response({'msg': 'Equipment not found'}, status=status.HTTP_404_NOT_FOUND)
    def post(self, request):
        try:
            equipment = request.data
            equipment['company'] = request.user.company.id
            print(equipment)
            serializer = serializers.EquipmentSerializer(data=equipment)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



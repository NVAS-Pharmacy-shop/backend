import asyncio
import datetime
import threading
from io import BytesIO

import qrcode
from django.core.mail import send_mail, EmailMessage
from django.db.models import Prefetch, Q, F
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.utils.html import strip_tags
from rest_framework.response import Response
# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from . import models
from . import serializers
from rest_framework.permissions import IsAuthenticated
from auth.custom_permissions import IsCompanyAdmin, IsSystemAdmin
from shared.mixins import PermissionPolicyMixin
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from multiprocessing import Process
from user.models import User

from .mail import send_reservation_email


class Reserve_equipment(PermissionPolicyMixin, APIView):
    permission_classes_per_method = {
        "post": [IsAuthenticated],
    }

    def post(self, request):
        user = request.user
        reserved_equipments = request.data['equipments']
        company_id = None
        if 'company_id' in request.data:
            company_id = request.data['company_id']
        date = None
        if 'date' in request.data:
            date = request.data['date']
        pickup_schedule_id = None
        if 'pickup_schedule_id' in request.data:
            pickup_schedule_id = request.data['pickup_schedule_id']

        equipments = []

        for reserved_equipment in reserved_equipments:
            try:
                equipment_id = reserved_equipment['equipment_id']
                equipment = models.Equipment.objects.get(id=equipment_id)
                if equipment.company_id != company_id:
                    return Response({'error': 'wrong_item'}, status=status.HTTP_400_BAD_REQUEST)
            except models.Equipment.DoesNotExist:
                return Response({'error': 'Equipment not found'}, status=status.HTTP_404_NOT_FOUND)
            quantity = reserved_equipment['quantity']
            if equipment.quantity < quantity:
                return Response({'error': 'Not enough equipment'}, status=status.HTTP_400_BAD_REQUEST)

            equipments.append(tuple((equipment, quantity)))

        pickup_schedule_exists = models.PickupSchedule.objects.filter(id=pickup_schedule_id).exists()

        if not pickup_schedule_exists and pickup_schedule_id:
            return Response({'error': 'Pickup schedule not found'}, status=status.HTTP_404_NOT_FOUND)

        if pickup_schedule_id and date != None:
            return Response({'error': 'Pickup schedule and date cannot be both specified'}, status=status.HTTP_400_BAD_REQUEST)

        with atomic():
            reservation = models.EquipmentReservation.objects.create(
                user=user,
                status=models.EquipmentReservation.EquipmentStatus.PENDING,
            )
            if pickup_schedule_exists:
                pickup_schedule = models.PickupSchedule.objects.get(id=pickup_schedule_id)
                reservation.pickup_schedule = pickup_schedule
                reservation.save()
            else:
                date = parse_datetime(date)
                duration = (datetime.timedelta(minutes=30) + datetime.datetime.min).time()

                admins_not_free = models.PickupSchedule.objects.exclude(
                    Q(company_id=company_id,),
                    Q(start_time__gt=date.time()-F('duration_minutes')),
                    Q(start_time__gt=duration-F('duration_minutes')),
                    Q(start_time__range=(date.time(), duration))
                ).filter(date__exact=date.date())
                non_free_ids = [admin.company_admin_id for admin in admins_not_free]
                print(non_free_ids)
                non_free_ids = list(set(non_free_ids))
                admins_free = User.objects.filter(company_id=company_id).exclude(id__in=non_free_ids)
                if admins_free.exists():
                    pickup_schedule = models.PickupSchedule.objects.create(
                        company_id=company_id,
                        date=date.date(),
                        start_time=date.time(),
                        duration_minutes=duration,
                        company_admin=admins_free.first(),
                    )
                    pickup_schedule.save()
                else:
                    return Response({'error': 'No company admin is available at this time'}, status=status.HTTP_400_BAD_REQUEST)

                reservation.pickup_schedule = pickup_schedule
                reservation.save()


            for equipment, quantity in equipments:
                equipment.quantity -= quantity
                equipment.save()
                models.ReservedEquipment.objects.create(
                    reservation=reservation,
                    equipment=equipment,
                    quantity=quantity,
                ).save()

        email_thread = threading.Thread(target=send_reservation_email, args=(reservation.id, user.email))
        email_thread.start()


        return Response({'msg': 'Equipment reserved', 'reservation': reservation.id}, status=status.HTTP_200_OK)

class Company(PermissionPolicyMixin, APIView):
    permission_classes_per_method = {
        "get": [IsAuthenticated],
        "put": [IsAuthenticated, IsCompanyAdmin],
        "post": [IsSystemAdmin],
    }

    def get(self, request, id=None):
        if (id==None):
            if(request.user.role.__eq__('company_admin') and False):
                try:
                    company = models.Company.objects.get(admin=request.user.id)
                    serializer = serializers.CompanySerializer(company)
                    return Response({'msg': 'get company', 'company': serializer.data}, status=status.HTTP_200_OK)
                except models.Company.DoesNotExist:
                    return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                queryparams = request.query_params
                filters = {}
                if 'name' in queryparams and queryparams['name'] != '':
                    filters['name__icontains'] = queryparams['name']
                if 'rating' in queryparams and queryparams['rating'] != '':
                    filters['rate__gte'] = queryparams['rating']

                companies = models.Company.objects.filter(**filters)
                serializer = serializers.CompanySerializer(companies, many=True)
                return Response({'msg': 'get all companies', 'company': serializer.data}, status=status.HTTP_200_OK)
        elif id:
            try:
                company = get_object_or_404(models.Company.objects.prefetch_related(
                    Prefetch('pickup_schedules', queryset=models.PickupSchedule.objects.filter(equipment_reservation__isnull=True),
                             to_attr='filtered_pickup_schedules'),
                ), id=id)
                serializer = serializers.FullInfoCompanySerializer(company)
                return Response({'msg': 'get company', 'company': serializer.data}, status=status.HTTP_200_OK)
            except models.Company.DoesNotExist:
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        try:
            company = models.Company.objects.get(id=id)
        except models.Company.DoesNotExist:
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
        "post": [IsAuthenticated]#, IsCompanyAdmin]
    }
    def get(self, request, id=None):
        try:
            if id is None:
                schedules = models.PickupSchedule.objects.filter(company_id=request.user.company.id)
                serializer = serializers.PickupScheduleSerializer(schedules, many=True)
                return Response({'msg': 'get schedules', 'schedules': serializer.data}, status=status.HTTP_200_OK)
            else:
                schedule = models.PickupSchedule.objects.get(company_id=id)
                serializer = serializers.PickupScheduleSerializer(schedule, many=True)
                return Response({'msg': 'get schedule', 'schedule': serializer.data}, status=status.HTTP_200_OK)
        except models.PickupSchedule.DoesNotExist:
            raise Http404("Schedule not found")
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            pickup_data = {}
            data = request.data

            admin = User.objects.get(first_name__iexact=data['first_name'], last_name__iexact=data['last_name'])

            pickup_data['company_admin'] = admin
            pickup_data['date'] = data['date']
            pickup_data['start_time'] = data['start_time']
            pickup_data['duration_minutes'] = (datetime.timedelta(minutes=data['duration_minutes']) + datetime.datetime.min).time()
            pickup_data['company'] = admin.company

            pickup_schedule = models.PickupSchedule.objects.create(**pickup_data)
            return Response({'msg': 'create schedule', 'schedule': pickup_schedule.id}, status=status.HTTP_201_CREATED)

            # serializer = serializers.PickupScheduleSerializer(**pickup_data)
            # if serializer.is_valid():
            #     serializer.save()
            #     print("serializer data:", serializer.data)
            #     return Response(serializer.data, status=status.HTTP_201_CREATED)
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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

    def delete(self, request, id=None):
        try:
            if id is not None and request.user.role == 'company_admin':
                # add checking if the schedule is created by user!
                equipment = models.Equipment.objects.get(id=id)
                equipment.delete()
                return Response({'msg': 'Equipment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'Equipment ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        except models.PickupSchedule.DoesNotExist:
            raise Http404("Schedule not found")
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

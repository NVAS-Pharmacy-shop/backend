import datetime
from io import BytesIO

import qrcode
from django.core.mail import send_mail, EmailMessage
from django.db.transaction import atomic
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
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
from drf_yasg.utils import swagger_auto_schema

from .serializers import EquipmentSerializer


class Reserve_equipment(PermissionPolicyMixin, APIView):
    permission_classes_per_method = {
        "post": [IsAuthenticated],
    }

    def post(self, request):
        user = request.user
        reserved_equipments = request.data['equipments']
        company_id = request.data['company_id']
        date = parse_datetime(request.data['date'])

        # if date < datetime.datetime.now():
        #     return Response({'error': 'Date is in the past'}, status=status.HTTP_400_BAD_REQUEST)

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


        with atomic():
            reservation = models.EquipmentReservation.objects.create(
                user=user,
                date=datetime.datetime.now(),
                status=models.EquipmentReservation.EquipmentStatus.PENDING,
            )


            print(equipments)
            for equipment, quantity in equipments:
                equipment.quantity -= quantity
                equipment.save()
                models.ReservedEquipment.objects.create(
                    reservation=reservation,
                    equipment=equipment,
                    quantity=quantity,
                ).save()

        send_reservation_email(reservation.id, user.email)


        return Response({'msg': 'Equipment reserved', 'reservation': reservation.id}, status=status.HTTP_200_OK)


def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save the image to a BytesIO buffer
    buffer = BytesIO()
    img.save(buffer)
    return buffer.getvalue()

def send_reservation_email(reservation_id, recipient_email):
    # Generate QR code
    # get with joins
    reservation_info = models.EquipmentReservation.objects.get(id=reservation_id)

    qr_code_data = (f'Reservation ID: {reservation_info.id}\n'
                    f'\tUser: {reservation_info.user.email}\n'
                    f'\tDate: {reservation_info.date}\n')

    for reserved_equipment in reservation_info.reserved_equipment.all():
        qr_code_data += f'\t{reserved_equipment.equipment.name} x {reserved_equipment.quantity}\n'


    qr_code_image = generate_qr_code(qr_code_data)




    # Create an email message with the QR code attached
    subject = 'Reservation Confirmation'
    message = render_to_string('reservation_email.html', {'reservation_info': qr_code_data})
    plain_message = strip_tags(message)

    email = EmailMessage(
        subject,
        plain_message,
        to=[recipient_email],
    )


    # Attach the QR code image
    email.attach('reservation_qr_code.png', qr_code_image, 'image/png')

    # Send the email
    email.send()


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
            filters = {}
            if 'name' in request.GET and request.GET['name'] != '':
                filters['name__icontains'] = request.GET['name']
            if 'rating' in request.GET and request.GET['rating'] != '':
                filters['rate__gte'] = request.GET['rating']

            companies = models.Company.objects.filter(**filters)

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
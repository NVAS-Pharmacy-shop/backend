from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist

from .serializers import CompanyAdminSerializer, UserSerializer
from user.models import User
from company.models import Company

from datetime import datetime


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        print('eeee')
        serializer.save()
        user = User.objects.get(email=request.data['email'])
        user.set_password(request.data['password'])
        user.is_active = False
        user.role = 'employee'
        user.save()

        confirmation_token = default_token_generator.make_token(user)
        activate_link_url = 'http://localhost:8000/api/auth/activate_token'
        actiavation_link = f'{activate_link_url}?user_id={user.id}&confirmation_token={confirmation_token}'

        send_mail(
        "ACTIVATE ACCOUNT",
        actiavation_link,
        "slobodanobradovic3@gmail.com",
        [str(user.email)],
        fail_silently=False,
        )

        return Response({'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_200_OK)

@api_view(['POST'])
def registerCompanyAdmin(request):
    serializer = CompanyAdminSerializer(data=request.data)
    if serializer.is_valid():       
        serializer.save()
        try:
            user = User.objects.get(email=request.data['email'])
            company = Company.objects.get(id=request.data['company'])
        except ObjectDoesNotExist:
            return Response({'error': 'Company does not exist'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(request.data['password'])
        user.is_active = True
        user.role = 'company_admin'
        user.company = company
        user.save()
        return Response({'user': serializer.data}, status=status.HTTP_201_CREATED)

    if User.objects.filter(email=request.data['email']).exists():
        return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST) 
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def activate(request):

    user_id = request.query_params.get('user_id', '')
    confirmation_token = request.query_params.get('confirmation_token', '')
    try:
        user = User.objects.get(pk=user_id)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is None:
        return Response('User not found', status=status.HTTP_400_BAD_REQUEST)
    if not default_token_generator.check_token(user, confirmation_token):
        return Response('Token is invalid or expired. Please request another confirmation email by signing in.', status=status.HTTP_400_BAD_REQUEST)
    user.is_active = True
    user.save()
    return Response('Email successfully confirmed')

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        user.last_login = datetime.now()
        user.save()
        token = super().get_token(user)

        # Token embedded fields
        token['email'] = user.email
        token['role'] = user.role

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
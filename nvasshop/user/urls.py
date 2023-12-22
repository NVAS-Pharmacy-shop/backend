from django.urls import path
from .views import User, CompanyAdmin_PasswordChange
from .views import CompanyAdmin
urlpatterns = [
    path('user/', User.as_view()),
    path('user/<int:id>/', User.as_view()),
    path('user/admins/companies/', CompanyAdmin.as_view(), name='user-admins'),
    path('user/admins/', CompanyAdmin.as_view(), name='user-admin'),
    path('user/admins/updatePassword/', CompanyAdmin_PasswordChange.as_view(), name='user-admin-password-change'),
]
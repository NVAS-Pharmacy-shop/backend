from django.urls import path
from .views import User
from .views import CompanyAdmin
urlpatterns = [
    path('user/', User.as_view()),
    path('user/<int:id>/', User.as_view()),
    path('user/admins/<int:company_id>/', CompanyAdmin.as_view(), name='user-admins'),
    path('user/admins/', CompanyAdmin.as_view(), name='user-admin'),
    path('user/admins/updatePassword', CompanyAdmin.as_view(), name='user-admin'),
]
from django.urls import path
from .views import CompanyAdminCompanyId, User, CompanyAdmin_PasswordChange
from .views import CompanyAdmin
app_name = "user"
urlpatterns = [
    path('', User.as_view()),
    path('<int:id>/', User.as_view()),
    path('admins/companies/', CompanyAdmin.as_view(), name='admins'),
    path('admins/', CompanyAdmin.as_view(), name='admin'),
    path('admins/updatePassword/', CompanyAdmin_PasswordChange.as_view(), name='admin-password-change'),
    path('admins/companyId/', CompanyAdminCompanyId.as_view(), name='admin-company-id'),
]
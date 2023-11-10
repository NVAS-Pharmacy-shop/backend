from django.urls import path

from . import views
from .views import Company

app_name = "company"
urlpatterns = [
    path("all/", Company.as_view(), name='company-get'),
    path("updateCompany/<int:id>/", Company.as_view(), name='company-update'),
]
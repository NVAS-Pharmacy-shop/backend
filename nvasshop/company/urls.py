from django.urls import path

from . import views
from .views import Company, Equipment

app_name = "company"
urlpatterns = [
    path("<int:id>/", Company.as_view(), name="company-detail"),
    path("", Company.as_view(), name="company-list"),
    path("equipment/", Equipment.as_view(), name="equipment-list"),
    path("base_info/<int:id>/", views.CompanyBaseInfo.as_view(), name="company-base-info-detail"),
    path("base_info/", views.CompanyBaseInfo.as_view(), name="company-base-info-list"),
    path("create-schedule/", views.PickupSchedule.as_view(), name="create-schedule"),
    path("schedules/<int:id>/", views.PickupSchedule.as_view(), name="get-schedule"),
    path("schedules/", views.PickupSchedule.as_view(), name="get-schedule"),
    path("equipment/admin/", views.Equipment_CompanyAdmin.as_view(), name="equipment-admin-list"),
    path("equipment/admin/<int:id>/", views.Equipment_CompanyAdmin.as_view(), name="equipment-admin-detail"),
]

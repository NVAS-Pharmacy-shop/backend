from django.urls import path

from . import views
from .views import Company, Equipment, Reserve_equipment

app_name = "company"
urlpatterns = [
    path("<int:id>/", Company.as_view(), name="company-detail"),
    path("", Company.as_view(), name="company-list"),
    path("equipment/", Equipment.as_view(), name="equipment-list"),
    path("base_info/<int:id>/", views.CompanyBaseInfo.as_view(), name="company-base-info-detail"),
    path("base_info/", views.CompanyBaseInfo.as_view(), name="company-base-info-list"),
    path("reserve/", Reserve_equipment.as_view()),
    path("create-schedule/", views.PickupSchedule.as_view(), name="create-schedule"),
    path("schedules/<int:id>/", views.PickupSchedule.as_view(), name="get-schedule"),
    path("schedules/", views.PickupSchedule.as_view(), name="get-schedule"),
    path("equipment/admin/", views.Equipment_CompanyAdmin.as_view(), name="equipment-admin-list"),
    path("reserve/", Reserve_equipment.as_view()),
    path("equipment/admin/<int:id>/", views.Equipment_CompanyAdmin.as_view(), name="equipment-admin-detail"),
    path("reservations/<str:date_str>/<str:period>/", views.CompanyReservations.as_view(), name="company-reservations"),
    path("admin/", views.CompanyAdmin.as_view(), name="admin-company"),
    path("company_customers/", views.CompanyCustomers.as_view(), name="company-customers"),
    path("delivered-equipment/<int:id>/", views.HandlingEquipmentReservation.as_view(), name="delivered-equipment"),
    path("reservations/", views.HandlingEquipmentReservation.as_view(), name="reservations")
]

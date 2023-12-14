from django.urls import path

from . import views
from .views import Company, Equipment

app_name = "company"
urlpatterns = [
    path("<int:id>", Company.as_view()),
    path("", Company.as_view()),
    path("equipment/", Equipment.as_view()),
    path("base_info/<int:id>", views.CompanyBaseInfo.as_view()),
    path("base_info/", views.CompanyBaseInfo.as_view()),
    path("create-schedule", views.PickupSchedule.as_view())
]
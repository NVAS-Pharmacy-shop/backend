from django.urls import path

from . import views
from .views import Company, Equipment

app_name = "company"
urlpatterns = [
    path("<int:id>", Company.as_view()),
    path("", Company.as_view()),
    path("equipment/", Equipment.as_view()),
]
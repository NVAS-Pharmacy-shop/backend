from django.urls import path

from . import views
from .views import Company

app_name = "company"
urlpatterns = [
    path("<int:id>", Company.as_view()),
    path("", Company.as_view()),
]
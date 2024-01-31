from django.urls import path

from . import views

app_name = "locationsim"
urlpatterns = [
    path("coordinates/", views.RouteCoordinates.as_view(), name="coordinates"),
]
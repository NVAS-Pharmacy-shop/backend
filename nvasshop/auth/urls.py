from django.urls import path
from . import views
from .views import MyTokenObtainPairView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', views.signup),
    path('registerCompanyAdmin/', views.registerCompanyAdmin),
    path('registerSystemAdmin/', views.registerSystemAdmin),
    path('activate_token/', views.activate, name='activate_token'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
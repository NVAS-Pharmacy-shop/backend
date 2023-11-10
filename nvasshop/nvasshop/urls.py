from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('user.urls')),
    path('api/company/', include('company.urls')),
    path('api/auth/', include('auth.urls'))
]

from django.contrib import admin
from django.urls import path, include

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from . import views


schema_view = get_schema_view(
    openapi.Info(
        title="NVAS API",
        default_version='v1',
        description="NVAS API",
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('user.urls')),
    path('api/company/', include('company.urls')),
    path('api/auth/', include('auth.urls')),
    path('api/swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger'),
]

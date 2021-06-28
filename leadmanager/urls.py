from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="AUTH API",
      default_version='v1',
      description="Authentication REST API with two family of users: teacher & student",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Local
    path('api/auth/', include('authentication.urls')),
    path('api/course/', include('course.urls')),
    # 3rd party
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('browsableAPI-auth/', include('rest_framework.urls')),
]

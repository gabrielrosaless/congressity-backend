"""backendTesis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() functurlpatterns = [ion: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include , re_path

#Imports para swagger
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Documentacion API Congressity",
      default_version='v0.1',
      description="Documentacion de API publica de Congressity",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="gabrielpprosales@gmai.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('api/', include('usuarios.urls')),
    path('articulos/', include('articulos.urls')),
    path('congresos/', include('congresos.urls')),
    path('inscripciones/', include('inscripciones.urls')),
    path('certificados/', include('certificados.urls')),
    path('estadisticas/', include('estadisticas.urls')),
    path('eventos/', include('eventos.urls'))
]

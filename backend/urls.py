from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework_simplejwt.views import TokenRefreshView

from django.shortcuts import render

#إضافة Swagger
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

def home(request):
    return render(request, 'index.html')
urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

path(
    'api/docs/',
    SpectacularSwaggerView.as_view(url_name='schema'),
    name='swagger-ui'
),

path(
    'api/redoc/',
    SpectacularRedocView.as_view(url_name='schema'),
    name='redoc'
),

    path('admin/', admin.site.urls),

     # ✅ accounts APIs (register + login + admin login)
    path('api/', include('accounts.urls')),

    # contact APIs
    path('api/', include('contact.urls')),

    # refresh token
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

   path('', home),
  
]
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import AdminLoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ accounts APIs (login + register)
    path('api/', include('accounts.urls')),

    # ✅ Admin-only login
    path('api/admin/login/', AdminLoginView.as_view()),

    # contact APIs
    path('api/', include('contact.urls')),

    # refresh token
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', lambda request: HttpResponse("Backend is running 🚀")),
]
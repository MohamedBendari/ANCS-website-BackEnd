from django.urls import path
from .views import RegisterView, LoginView, AdminLoginView

urlpatterns = [
    path('register/', RegisterView.as_view()),  # POST /api/register/
    path('login/',    LoginView.as_view()),      # POST /api/login/
    path('admin/login/', AdminLoginView.as_view()),  # POST /api/admin/login/
]

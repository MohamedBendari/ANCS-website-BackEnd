from django.urls import path
from .views import RegisterView, LoginView, AdminLoginView

urlpatterns = [
    path('register/', RegisterView.as_view()),  # POST /api/auth/register/
    path('login/',    LoginView.as_view()),      # POST /api/auth/login/
]

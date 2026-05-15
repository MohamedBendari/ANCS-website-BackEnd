from django.urls import path
from .views import RegisterView, LoginView, AdminLoginView, google_login, UsersListView, DeleteUserView, UpdateUserView
urlpatterns = [
    path('register/', RegisterView.as_view()),  # POST /api/register/
    path('login/',    LoginView.as_view()),      # POST /api/login/
    path('admin/login/', AdminLoginView.as_view()),  # POST /api/admin/login/
    # 🔥 Google Login
    path('auth/google/', google_login),

    # Users Management
    path('users/', UsersListView.as_view()),

    path('users/<int:user_id>/delete/', DeleteUserView.as_view()),

     path('users/<int:user_id>/update/', UpdateUserView.as_view()),
]

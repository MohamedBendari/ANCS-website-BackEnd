from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Profile
from .serializers import RegisterSerializer


# Register — أي حد يقدر يسجل
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


# Login موحد — بيرجع token + role + username
class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            role = user.profile.role
        except Profile.DoesNotExist:
            role = 'admin' if user.is_superuser else 'user'

        refresh = RefreshToken.for_user(user)

        return Response({
            "access":   str(refresh.access_token),
            "refresh":  str(refresh),
            "role":     role,
            "username": user.username,
        })


# Admin Login — للحماية الإضافية
class AdminLoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            role = user.profile.role
        except Profile.DoesNotExist:
            role = 'admin' if user.is_superuser else 'user'

        if role != 'admin':
            return Response(
                {"error": "Access denied. Admin only."},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access":   str(refresh.access_token),
            "refresh":  str(refresh),
            "role":     role,
            "username": user.username,
        })
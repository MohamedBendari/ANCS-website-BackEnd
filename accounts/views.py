from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Profile
from .serializers import RegisterSerializer


def authenticate_user(identifier, password):
    if not identifier or not password:
        return None

    user = None
    if '@' in identifier:
        try:
            user_obj = User.objects.get(email=identifier)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
    else:
        user = authenticate(username=identifier, password=password)

    print(f"DEBUG: Trying to authenticate {identifier} with password. User found: {user is not None}")
    return user


def get_login_fields(request):
    identifier = (
        request.data.get('username')
        or request.data.get('email')
        or request.data.get('user')
        or request.data.get('userName')
        or request.data.get('user_name')
        or request.data.get('full_name')
        or request.data.get('fullName')
        or request.data.get('name')
        or request.data.get('first_name')
        or request.data.get('firstName')
        or request.data.get('fullname')
    )
    if not identifier:
        for key, value in request.data.items():
            if key not in ('password', 'pass', 'password1') and value:
                identifier = value
                break

    password = (
        request.data.get('password')
        or request.data.get('pass')
        or request.data.get('password1')
        or request.data.get('pwd')
    )
    return identifier, password


# Register — أي حد يقدر يسجل
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


# Login موحد — بيرجع token + role + username
class LoginView(APIView):
    def post(self, request):
        identifier, password = get_login_fields(request)

        print(f"DEBUG: Login attempt - identifier: {identifier}, password provided: {bool(password)}")

        if not identifier or not password:
            return Response(
                {
                    "error": "Username/email and password are required",
                    "received_fields": list(request.data.keys()),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate_user(identifier, password)

        if user is None:
            return Response(
                {
                    "error": "Invalid credentials",
                    "received_fields": list(request.data.keys()),
                },
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
        identifier, password = get_login_fields(request)

        if not identifier or not password:
            return Response(
                {
                    "error": "Username/email and password are required",
                    "received_fields": list(request.data.keys()),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate_user(identifier, password)

        if user is None:
            return Response(
                {
                    "error": "Invalid credentials",
                    "received_fields": list(request.data.keys()),
                },
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
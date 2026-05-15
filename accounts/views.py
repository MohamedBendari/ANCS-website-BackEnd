from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view

from google.oauth2 import id_token
from google.auth.transport import requests

from .models import Profile
from .serializers import RegisterSerializer,UserManagementSerializer
from django.conf import settings


# 🔥 حط هنا الـ Client ID بتاع Google
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID 


def authenticate_user(identifier, password):

    if not identifier or not password:
        return None

    user = None

    if '@' in identifier:

        try:
            user_obj = User.objects.get(email=identifier)

            user = authenticate(
                username=user_obj.username,
                password=password
            )

        except User.DoesNotExist:
            user = None

    else:

        user = authenticate(
            username=identifier,
            password=password
        )

    print(
        f"DEBUG: Trying to authenticate {identifier} "
        f"with password. User found: {user is not None}"
    )

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


# ✅ Register
class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = RegisterSerializer


# ✅ Normal Login
class LoginView(APIView):

    def post(self, request):

        identifier, password = get_login_fields(request)

        print(
            f"DEBUG: Login attempt - identifier: {identifier}, "
            f"password provided: {bool(password)}"
        )

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
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": role,
            "username": user.username,
        })


# ✅ Admin Login
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
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": role,
            "username": user.username,
        })


# 🔥 Google Login
@api_view(['POST'])
def google_login(request):

    token = request.data.get("token")

    if not token:

        return Response(
            {"error": "Google token is required"},
            status=400
        )

    try:

        # verify token from google
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get('email')
        name = idinfo.get('name', '')

        if not email:

            return Response(
                {"error": "Email not found"},
                status=400
            )

        # create user if not exists
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": name
            }
        )

        # create profile if not exists
        Profile.objects.get_or_create(
            user=user,
            defaults={
                "role": "user"
            }
        )

        # get role
        try:
            role = user.profile.role

        except Profile.DoesNotExist:
            role = 'user'

        # generate JWT
        refresh = RefreshToken.for_user(user)

        return Response({

            "message": "Google login successful",

            "access": str(refresh.access_token),
            "refresh": str(refresh),

            "role": role,

            "username": user.username,

            "email": user.email,

            "name": user.first_name,

            "new_user": created
        })

    except ValueError:

        return Response(
            {"error": "Invalid Google token"},
            status=status.HTTP_400_BAD_REQUEST
        )

# ✅ Get All Users
class UsersListView(APIView):

    def get(self, request):

        users = User.objects.all().order_by('-date_joined')

        serializer = UserManagementSerializer(
            users,
            many=True
        )

        return Response(serializer.data)


# ✅ Delete User
class DeleteUserView(APIView):

    def delete(self, request, user_id):

        try:

            user = User.objects.get(id=user_id)

            user.delete()

            return Response({
                "message": "User deleted successfully"
            })

        except User.DoesNotExist:

            return Response(
                {"error": "User not found"},
                status=404
            )


# ✅ Update User
class UpdateUserView(APIView):

    def put(self, request, user_id):

        try:

            user = User.objects.get(id=user_id)

        except User.DoesNotExist:

            return Response(
                {"error": "User not found"},
                status=404
            )

        # update basic data
        user.username = request.data.get(
            'username',
            user.username
        )

        user.email = request.data.get(
            'email',
            user.email
        )

        user.is_active = request.data.get(
            'is_active',
            user.is_active
        )

        user.save()

        # update role
        role = request.data.get('role')

        if role:

            profile, created = Profile.objects.get_or_create(
                user=user
            )

            profile.role = role

            profile.save()

        serializer = UserManagementSerializer(user)

        return Response(serializer.data)
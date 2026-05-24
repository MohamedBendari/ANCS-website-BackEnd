from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from .models import Profile
from .serializers import RegisterSerializer, UserManagementSerializer
from django.conf import settings
from openai import OpenAI

GOOGLE_CLIENT_ID = getattr(settings, "GOOGLE_CLIENT_ID", "")


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
        if not identifier or not password:
            return Response(
                {"error": "Username/email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = authenticate_user(identifier, password)
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
                {"error": "Username/email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = authenticate_user(identifier, password)
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
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": role,
            "username": user.username,
        })


# ✅ Google Login
@api_view(['POST'])
def google_login(request):
    token = request.data.get("token")

    if not token:
        return Response({"error": "Google token is required"}, status=400)

    try:
        # ✅ verify token
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10  # يتحمل فرق توقيت بسيط
        )

        email = idinfo.get('email')
        name  = idinfo.get('name', '')

        if not email:
            return Response({"error": "Email not found in token"}, status=400)

        # ✅ create or get user
        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email, "first_name": name}
        )

        # ✅ create profile if not exists
        Profile.objects.get_or_create(user=user, defaults={"role": "user"})

        try:
            role = user.profile.role
        except Profile.DoesNotExist:
            role = 'user'

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Google login successful",
            "access":    str(refresh.access_token),
            "refresh":   str(refresh),
            "role":      role,
            "username":  user.username,
            "email":     user.email,
            "name":      user.first_name,
            "new_user":  created
        })

    except ValueError as e:
        # ✅ token invalid or expired
        print("GOOGLE TOKEN ERROR:", str(e))
        return Response(
            {"error": f"Invalid Google token: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        # ✅ any other error
        print("GOOGLE UNEXPECTED ERROR:", str(e))
        return Response(
            {"error": f"Server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ✅ Get All Users
class UsersListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        serializer = UserManagementSerializer(users, many=True)
        return Response(serializer.data)


# ✅ Delete User
class DeleteUserView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({"message": "User deleted successfully"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


# ✅ Update User
class UpdateUserView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        user.username  = request.data.get('username',  user.username)
        user.email     = request.data.get('email',     user.email)
        user.is_active = request.data.get('is_active', user.is_active)
        user.save()

        role = request.data.get('role')
        if role:
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()

        serializer = UserManagementSerializer(user)
        return Response(serializer.data)


# ✅ Change Password
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response(
                {"error": "Current password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(new_password) < 6:
            return Response(
                {"error": "Password must be at least 6 characters"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"})


# ✅ AI Chat
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    try:
        message = request.data.get("message")
        if not message:
            return Response({"error": "Message is required"}, status=400)

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are ANCS AI assistant. "
                        "Help users solve networking and system problems professionally."
                    )
                },
                {"role": "user", "content": message}
            ]
        )
        reply = response.choices[0].message.content
        return Response({"reply": reply})

    except Exception as e:
        return Response({"error": str(e)}, status=500)
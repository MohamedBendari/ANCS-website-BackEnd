from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class RegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    fullName = serializers.CharField(write_only=True, required=False, allow_blank=True)
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    user = serializers.CharField(write_only=True, required=False, allow_blank=True)
    userName = serializers.CharField(write_only=True, required=False, allow_blank=True)
    user_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    firstName = serializers.CharField(write_only=True, required=False, allow_blank=True)
    fullname = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password1 = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'username', 'full_name', 'fullName', 'name', 'user', 'userName', 'user_name',
            'first_name', 'firstName', 'fullname', 'email', 'password', 'password1'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        password = attrs.get('password') or attrs.get('password1')
        if not password:
            raise serializers.ValidationError({
                'password': 'Password is required.'
            })

        username = (
            attrs.get('username')
            or attrs.get('user')
            or attrs.get('userName')
            or attrs.get('user_name')
            or attrs.get('full_name')
            or attrs.get('fullName')
            or attrs.get('first_name')
            or attrs.get('firstName')
            or attrs.get('fullname')
            or attrs.get('name')
            or (attrs.get('email') or '').split('@')[0]
        )

        if not username:
            raise serializers.ValidationError({
                'username': 'Username, full name, or email is required.'
            })

        attrs['username'] = username
        attrs['password'] = password
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class UserManagementSerializer(serializers.ModelSerializer):

    role = serializers.CharField(source='profile.role')

    class Meta:

        model = User

        fields = [
            'id',
            'username',
            'email',
            'role',
            'date_joined',
            'is_active',
        ]
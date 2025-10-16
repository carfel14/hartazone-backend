from __future__ import annotations

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active',
            'date_joined',
        )
        read_only_fields = ('id', 'email', 'role', 'is_active', 'date_joined')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    name = serializers.CharField()
    role = serializers.ChoiceField(
        choices=[
            (User.Roles.USER, 'User'),
            (User.Roles.DRIVER, 'Driver'),
            (User.Roles.BUSINESS, 'Business'),
        ],
        default=User.Roles.USER,
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'name', 'role')

    def create(self, validated_data):
        password = validated_data.pop('password')
        name = validated_data.pop('name', '').strip()
        first_name, last_name = self._split_name(name)
        user = User.objects.create_user(
            password=password,
            first_name=first_name,
            last_name=last_name,
            **validated_data,
        )
        return user

    @staticmethod
    def _split_name(name: str) -> tuple[str, str]:
        if not name:
            return '', ''
        parts = name.split()
        if len(parts) == 1:
            return parts[0], ''
        return parts[0], ' '.join(parts[1:])


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Unable to log in with provided credentials.')
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')
        attrs['user'] = user
        return attrs


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class SocialLoginSerializer(serializers.Serializer):
    PROVIDER_CHOICES = (
        ('google', 'Google'),
        ('apple', 'Apple'),
    )

    provider = serializers.ChoiceField(choices=PROVIDER_CHOICES)
    id_token = serializers.CharField(write_only=True, required=False, allow_blank=True)
    access_token = serializers.CharField(write_only=True, required=False, allow_blank=True)
    role = serializers.ChoiceField(
        choices=[
            (User.Roles.USER, 'User'),
            (User.Roles.DRIVER, 'Driver'),
            (User.Roles.BUSINESS, 'Business'),
        ],
        default=User.Roles.USER,
    )
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        provider = attrs.get('provider')
        id_token = attrs.get('id_token')
        access_token = attrs.get('access_token')

        if provider == 'google' and not id_token:
            raise serializers.ValidationError({'id_token': 'Google login requires an ID token.'})
        if provider == 'apple' and not id_token:
            raise serializers.ValidationError({'id_token': 'Apple login requires an identity token.'})
        if not id_token and not access_token:
            raise serializers.ValidationError('You must supply either an ID token or access token.')
        return attrs

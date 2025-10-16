from __future__ import annotations

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import SocialAccount, User
from .providers import SocialVerificationError, verify_social_token
from .serializers import (
    RegisterSerializer,
    SocialLoginSerializer,
    UserSerializer,
    UserTokenObtainPairSerializer,
)


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        data = {
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({'detail': 'Invalid refresh token.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


class SocialLoginView(generics.GenericAPIView):
    serializer_class = SocialLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.validated_data['provider']
        id_token = serializer.validated_data.get('id_token')
        role = serializer.validated_data['role']

        try:
            profile = verify_social_token(provider, id_token)
        except SocialVerificationError as exc:
            return Response({'detail': exc.message}, status=status.HTTP_400_BAD_REQUEST)

        first_name = profile.first_name or serializer.validated_data.get('first_name') or ''
        last_name = profile.last_name or serializer.validated_data.get('last_name') or ''

        user = User.objects.filter(email__iexact=profile.email).first()
        created = False
        if not user:
            user = User.objects.create_user(
                email=profile.email,
                password=None,
                first_name=first_name,
                last_name=last_name,
                role=role,
            )
            created = True
        else:
            updates = {}
            if not user.first_name and first_name:
                updates['first_name'] = first_name
            if not user.last_name and last_name:
                updates['last_name'] = last_name
            if updates:
                for field, value in updates.items():
                    setattr(user, field, value)
                user.save(update_fields=list(updates.keys()))

        account, _ = SocialAccount.objects.get_or_create(
            provider=profile.provider,
            subject=profile.subject,
            defaults={'user': user},
        )
        if account.user != user:
            account.user = user
            account.save(update_fields=['user'])

        refresh = RefreshToken.for_user(user)
        data = {
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'provider': provider,
            'is_new': created,
        }
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(data, status=status_code)

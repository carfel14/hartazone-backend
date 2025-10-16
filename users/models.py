from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        USER = "user", _("User")
        DRIVER = "driver", _("Driver")
        BUSINESS = "business", _("Business")
        ADMIN = "admin", _("Admin")

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.USER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class SocialAccount(models.Model):
    class Providers(models.TextChoices):
        GOOGLE = "google", _("Google")
        APPLE = "apple", _("Apple")

    user = models.ForeignKey(User, related_name="social_accounts", on_delete=models.CASCADE)
    provider = models.CharField(max_length=32, choices=Providers.choices)
    subject = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("provider", "subject")
        verbose_name = _("social account")
        verbose_name_plural = _("social accounts")

    def __str__(self) -> str:
        return f"{self.provider}:{self.user.email}"

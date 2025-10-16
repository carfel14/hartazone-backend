import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Ensures a default administrative user exists."

    def handle(self, *args, **options):
        User = get_user_model()

        admin_email = os.environ.get('ADMIN_EMAIL', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin')
        admin_first_name = os.environ.get('ADMIN_FIRST_NAME', 'Admin')
        admin_last_name = os.environ.get('ADMIN_LAST_NAME', 'User')

        if not admin_email:
            self.stdout.write(self.style.WARNING('No ADMIN_EMAIL provided; skipping admin creation.'))
            return

        role_value = None
        if hasattr(User, 'Roles') and hasattr(User.Roles, 'ADMIN'):
            role_value = User.Roles.ADMIN

        with transaction.atomic():
            user, created = User.objects.get_or_create(
                email=User.objects.normalize_email(admin_email),
                defaults={
                    'first_name': admin_first_name,
                    'last_name': admin_last_name,
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                    **({'role': role_value} if role_value else {}),
                },
            )

            updated_fields: list[str] = []

            if created:
                user.set_password(admin_password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created admin user '{user.email}'."))
                return

            if admin_password and not user.check_password(admin_password):
                user.set_password(admin_password)
                updated_fields.append('password')

            if not user.is_staff:
                user.is_staff = True
                updated_fields.append('is_staff')

            if not user.is_superuser:
                user.is_superuser = True
                updated_fields.append('is_superuser')

            if role_value and getattr(user, 'role', None) != role_value:
                user.role = role_value
                updated_fields.append('role')

            if updated_fields:
                user.save(update_fields=updated_fields)
                self.stdout.write(self.style.SUCCESS(f"Updated admin user '{user.email}' ({', '.join(updated_fields)})."))
            else:
                self.stdout.write(f"Admin user '{user.email}' already up to date." )

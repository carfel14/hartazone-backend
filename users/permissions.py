from __future__ import annotations

from typing import Iterable, Sequence

from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    """
    Restrict access based on the authenticated user's role.

    Usage:
        class MyView(APIView):
            permission_classes = [RolePermission.for_roles({"admin", "business"})]
    """

    def __init__(self, allowed_roles: Iterable[str]):
        self.allowed_roles = frozenset(allowed_roles)

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if not self.allowed_roles:
            return True
        return getattr(user, "role", None) in self.allowed_roles

    @classmethod
    def for_roles(cls, roles: Sequence[str]) -> "RolePermission":
        """
        Convenience constructor so permission can be declared without
        overriding `permission_classes`.
        """
        return cls(roles)

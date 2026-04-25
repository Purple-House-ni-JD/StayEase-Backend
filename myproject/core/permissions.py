from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Allow access only to users with role='admin'."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsGuest(BasePermission):
    """Allow access only to users with role='guest'."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'guest'
        )


class IsAdminOrReadOnly(BasePermission):
    """Read-only for everyone; write access only for admins."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsOwnerOrAdmin(BasePermission):
    """Object-level: owner or admin only."""

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.role == 'admin':
            return True
        # Support objects with `user` FK or `user_id`
        owner = getattr(obj, 'user', None)
        return owner == request.user
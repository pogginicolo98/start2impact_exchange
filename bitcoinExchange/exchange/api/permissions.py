from rest_framework import permissions


class IsOwnerProfile(permissions.BasePermission):
    """
    * Users can only access their own data.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user.profile == obj.profile)


class IsActiveOrder(permissions.BasePermission):
    """
    * Users can only delete active orders.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.status

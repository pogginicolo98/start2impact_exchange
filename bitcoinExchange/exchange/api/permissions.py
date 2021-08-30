from rest_framework import permissions


class IsOwnerProfile(permissions.BasePermission):
    """
    * Users can only access their own data.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user.profile == obj.profile)

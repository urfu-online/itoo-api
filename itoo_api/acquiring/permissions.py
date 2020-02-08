from rest_framework import permissions


class OwnerPermission(permissions.BasePermission):
    """
    Object-level permission to only allow updating his own profile
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

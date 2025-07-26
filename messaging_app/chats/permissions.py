# Custom permissions for chats app
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to the owner of the object.
        return obj.user == request.user

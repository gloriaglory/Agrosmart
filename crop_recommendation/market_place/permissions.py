from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only allow owners of an object to edit/delete it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

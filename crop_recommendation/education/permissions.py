from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class IsAuthorOrAdmin(BasePermission):
    """Only the author (or an admin) can edit or delete a post or comment."""

    message = "Only the author or an admin can change this."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff or (obj.author_id is not None and obj.author_id == request.user.id)


# Kept for existing imports
IsCommentAuthorOrReadOnly = IsAuthorOrAdmin

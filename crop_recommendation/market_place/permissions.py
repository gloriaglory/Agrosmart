from django.conf import settings
from rest_framework import permissions


class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Anyone can browse. Only logged-in sellers (users with a NIDA number) can post.
    Set REQUIRE_NIDA_VERIFICATION=True once NIDA integration is live to also
    require a verified number.
    """
    message = "Only registered sellers with a NIDA number can post listings."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if not (user and user.is_authenticated and user.is_seller):
            return False
        if getattr(settings, 'REQUIRE_NIDA_VERIFICATION', False):
            return user.nida_verified
        return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only allow owners of an object to edit/delete it.
    """
    message = "You can only change your own listings."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller_id is not None and obj.seller_id == request.user.id

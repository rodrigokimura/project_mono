"""Mono's permissions"""
from rest_framework.permissions import BasePermission


class IsCreator(BasePermission):
    """Check if object was created by user"""

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

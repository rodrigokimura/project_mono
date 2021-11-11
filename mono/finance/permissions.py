from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsCreatorOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `created_by`.
        return obj.created_by == request.user

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and obj.user == request.user)
        )

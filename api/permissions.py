from rest_framework import permissions

SAFE_METHODS = ('GET', 'OPTIONS', 'HEAD')


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user == obj.user
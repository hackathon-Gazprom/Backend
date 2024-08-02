from rest_framework import permissions


class IsCurrentUserOrAdminPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff

from rest_framework import permissions
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='study-room-admin'):
            return True
        return False

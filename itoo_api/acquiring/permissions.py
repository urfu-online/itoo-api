from rest_framework import permissions
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)


class OwnerPermission(permissions.BasePermission):
    message = 'You must be the owner of this object.'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        logger.warn('''OwnerPermission: 
        obj: {}
        owner: {}
        user: {}'''.format(str(obj), str(obj.user), str(request.user)))

        return obj.user == request.user

import logging

# import jwt
# from django.conf import settings
# from django.contrib.auth.models import AnonymousUser
# from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission

logging.basicConfig()
logger = logging.getLogger(__name__)


# def get_user_by_jwt(request):
#     jwt_token = request.META.get('HTTP_AUTHORIZATION', None)
#     if jwt_token:
#         try:
#             token_data = jwt.decode(jwt_token, settings.SECRET_KEY)
#         except jwt.exceptions.ExpiredSignatureError:
#             return AnonymousUser
#         return User.objects.get(pk=token_data['user_id'])
#     else:
#         return request.user


# class IsGlobalManager(BasePermission):
#     def has_permission(self, request, view):
#         user = get_user_by_jwt(request)
#         if user and not user.is_anonymous:
#             return (user.employee.is_global_staff == 'global_staff') or user.is_superuser
#         else:
#             return False


class IsLoggedInUserOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff


class IsAdminUser(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff

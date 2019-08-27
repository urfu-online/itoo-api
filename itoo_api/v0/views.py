# pylint: disable=too-many-ancestors
"""
Views for itoo_api end points.
"""
import logging

from course_modes.models import CourseMode
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from courseware.courses import get_course_by_id
from organizations.models import Organization
from rest_framework import viewsets, status, permissions
from django.utils.decorators import method_decorator
from rest_framework.exceptions import NotFound
from rest_framework.response import Response as RESTResponse
from enrollment.serializers import CourseSerializer

from edx_rest_framework_extensions.authentication import JwtAuthentication
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from openedx.core.djangoapps.cors_csrf.authentication import SessionAuthenticationCrossDomainCsrf
from openedx.core.lib.api.permissions import ApiKeyHeaderPermission, ApiKeyHeaderPermissionIsAuthenticated
from openedx.core.djangoapps.cors_csrf.decorators import ensure_csrf_cookie_cross_domain
from openedx.core.lib.api.authentication import (
    OAuth2AuthenticationAllowInactiveUser,
    SessionAuthenticationAllowInactiveUser
)
from util.disable_rate_limit import can_disable_rate_limit

from student.models import CourseEnrollment
from xmodule.error_module import ErrorDescriptor
from xmodule.modulestore.django import modulestore

from itoo_api.models import Program, ProgramCourse, OrganizationCustom, OrganizationCourse
from itoo_api.serializers import ProgramSerializer, OrganizationSerializer, ProgramCourseSerializer, \
    CourseEnrollmentSerializer, UserEnrollmentSerializer, OrganizationCustomSerializer, OrganizationCourseSerializer

# from student.views import send_enrollment_email
logging.basicConfig()
logger = logging.getLogger(__name__)


class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    """Program view to fetch list programs data or single program
    using program short name.
    """
    queryset = Program.objects.filter(active=True)  # pylint: disable=no-member
    serializer_class = ProgramSerializer
    lookup_field = 'slug'


class ProgramCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Program view to fetch list programs data or single program
    using program short name.
    """
    queryset = Program.objects.filter(active=True)  # pylint: disable=no-member
    serializer_class = ProgramCourseSerializer
    lookup_field = 'slug'

    # def get_queryset(self):
    #     queryset = ProgramCourse.objects.filter(active=True)
    #     return queryset


# class ProgramCourseViewSet(viewsets.ReadOnlyModelViewSet):
#     """Program view to fetch list programs data or single program
#     using program short name.
#     """
#     queryset = ProgramCourse.objects.filter(active=True)  # pylint: disable=no-member
#     serializer_class = ProgramCourseSerializer
#     lookup_field = 'program_id'

# def get_queryset(self):
#     queryset = ProgramCourse.objects.filter(active=True)
#     return queryset

class OrganizationCustomViewSet(viewsets.ReadOnlyModelViewSet):
    """Program view to fetch list programs data or single program
    using program short name.
    """
    queryset = OrganizationCustom.objects.filter(active=True)  # pylint: disable=no-member
    serializer_class = OrganizationCustomSerializer
    lookup_field = 'slug'


class OrganizationCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Program view to fetch list programs data or single program
    using program short name.
    """
    queryset = OrganizationCustom.objects.filter(active=True)  # pylint: disable=no-member
    serializer_class = OrganizationCourseSerializer
    lookup_field = 'slug'


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """Program view to fetch list programs data or single program
    using program short name.
    """
    queryset = Organization.objects.filter(active=True)  # pylint: disable=no-member
    serializer_class = OrganizationSerializer
    lookup_field = 'short_name'


class ApiKeyPermissionMixIn(object):
    """
    This mixin is used to provide a convenience function for doing individual permission checks
    for the presence of API keys.
    """

    def has_api_key_permissions(self, request):
        """
        Checks to see if the request was made by a server with an API key.
        Args:
            request (Request): the request being made into the view
        Return:
            True if the request has been made with a valid API key
            False otherwise
        """
        return ApiKeyHeaderPermission().has_permission(request, self)


class EnrollmentUserThrottle(UserRateThrottle, ApiKeyPermissionMixIn):
    """Limit the number of requests users can make to the enrollment API."""
    rate = '40/minute'

    def allow_request(self, request, view):
        return self.has_api_key_permissions(request) or super(EnrollmentUserThrottle, self).allow_request(request, view)


@can_disable_rate_limit
class EnrollmentViewSet(APIView, ApiKeyPermissionMixIn):
    authentication_classes = (JwtAuthentication, OAuth2AuthenticationAllowInactiveUser,
                              SessionAuthenticationAllowInactiveUser,)
    permission_classes = ApiKeyHeaderPermissionIsAuthenticated,
    throttle_classes = EnrollmentUserThrottle,

    @method_decorator(ensure_csrf_cookie_cross_domain)
    def get(self, request, course_id=None, username=None):
        username = username or request.user.username

        # TODO Implement proper permissions
        if request.user.username != username and not self.has_api_key_permissions(request) \
                and not request.user.is_superuser:
            # Return a 404 instead of a 403 (Unauthorized). If one user is looking up
            # other users, do not let them deduce the existence of an enrollment.
            return RESTResponse(status=status.HTTP_404_NOT_FOUND)

        enrollment = CourseEnrollment.objects.get(user=username, course_id=course_id)

        if enrollment:
            return RESTResponse({'is_enrolled': True})

        return RESTResponse({'is_enrolled': False})


class PaidCoursesViewSet(APIView):

    def get(self, request, course_id=None):
        course_key = CourseKey.from_string(course_id)
        course = get_course_by_id(course_key)
        return RESTResponse({"course": str(course)})


class PaidCoursesViewSet2(viewsets.GenericViewSet):

    queryset = CourseOverview.objects.all # pylint: disable=no-member
    serializer_class = CourseSerializer
    lookup_field = 'course_id'

    # def get(self, request, course_id=None):
    #     course_key = CourseKey.from_string(course_id)
    #     course = get_course_by_id(course_key)
    #     return RESTResponse({"course": str(course)})
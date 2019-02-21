# pylint: disable=too-many-ancestors
"""
Views for itoo_api end points.
"""
from django.contrib.auth.models import User, AnonymousUser
from organizations.models import Organization
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import detail_route
from rest_framework.exceptions import NotFound
from opaque_keys.edx.keys import CourseKey
from rest_framework.response import Response as RESTResponse
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from opaque_keys import InvalidKeyError
from xmodule.modulestore.django import modulestore
from xmodule.error_module import ErrorDescriptor
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
# from student.views import send_enrollment_email

from itoo_api.models import Program, ProgramCourse
from itoo_api.serializers import ProgramSerializer, OrganizationSerializer, ProgramCourseSerializer, CourseEnrollmentSerializer, UserEnrollmentSerializer
from student.models import CourseEnrollment, CourseEnrollmentException, AlreadyEnrolledError, NonExistentCourseError, CourseEnrollmentAllowed
from course_modes.models import CourseMode

import logging
logger = logging.getLogger(__name__)


class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    """Program view to fetch list programs data or single program
    using program short name.
    """
    queryset = Program.objects.filter(active=True)  # pylint: disable=no-member
    serializer_class = ProgramSerializer
    lookup_field = 'short_name'


class ProgramCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Program view to fetch list programs data or single program
    using program short name.
    """
    queryset = ProgramCourse.objects.filter(active=True)  # pylint: disable=no-member
    serializer_class = ProgramCourseSerializer
    lookup_field = 'course_id'


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """Program view to fetch list programs data or single program
    using program short name.
    """
    queryset = Organization.objects.filter(active=True)  # pylint: disable=no-member
    serializer_class = OrganizationSerializer
    lookup_field = 'short_name'


class ApiKeyHeaderPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Check for permissions by matching the configured API key and header

        If settings.DEBUG is True and settings.EDX_API_KEY is not set or None,
        then allow the request. Otherwise, allow the request if and only if
        settings.EDX_API_KEY is set and the X-Edx-Api-Key HTTP header is
        present in the request and matches the setting.
        """
        # copied with some modifications from user_api
        api_key = getattr(settings, "EDX_API_KEY", '')
        return (
            (settings.DEBUG and not api_key) or
            (api_key and request.META.get("HTTP_X_EDX_API_KEY") == api_key)
        )


class ServerAPIViewSet(viewsets.GenericViewSet):
    authentication_classes = ()
    permission_classes = (ApiKeyHeaderPermission,)

    def _get_course_id(self, **kwargs):
        course_id_str = kwargs.get('course_id', None)
        try:
            course_key = CourseKey.from_string(course_id_str)
        except InvalidKeyError:
            raise NotFound(detail=u"Invalid course id '{}'".format(course_id_str))
        else:
            return course_key


class EnrollmentViewSet(ServerAPIViewSet):
    """
    API for retrieving and changing user course enrollments.
    User UID and course locator are used as lookup url parameters
    """
    serializer_class = UserEnrollmentSerializer

    lookup_field = 'course_id'

    ALLOWED_COURSE_MODES = (
        CourseMode.AUDIT,
        CourseMode.HONOR,
        CourseMode.VERIFIED,
        CourseMode.PROFESSIONAL,
        CourseMode.NO_ID_PROFESSIONAL_MODE,
        CourseMode.CREDIT_MODE,
    )

    def list(self, request, *args, **kwargs):
        enrollments = self._get_enrollments(*args, **kwargs)
        serializer = UserEnrollmentSerializer(enrollments, many=True, context={'request': request})
        return RESTResponse(serializer.data)

    @detail_route(methods=['post'])
    def enroll(self, request, *args, **kwargs):
        """
        Enroll student with forced mode

        Overrides enrollment mode for already enrolled student
        """
        user = self._get_user(*args, **kwargs)
        course_id = self._get_course_id(**kwargs)
        skip_enrollment_email = request.data.get('skip_enrollment_email', False)
        mode = request.data.get('mode', CourseMode.DEFAULT_MODE_SLUG)

        if mode not in self.ALLOWED_COURSE_MODES:
            return RESTResponse({'detail': u'Invalid course mode: {}'.format(mode)},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # create new enrollment
            logger.info("Create new enrollment: {} {}".format(user, course_id))
            CourseEnrollmentAllowed.objects.create(email=user.email, course_id=course_id)
            enrollment = CourseEnrollment.enroll(user, course_id, mode, check_access=True)
        except AlreadyEnrolledError:
            # update existing enrollment with current mode
            enrollment = CourseEnrollment.objects.get(user=user, course_id=course_id)
            enrollment.update_enrollment(is_active=True, mode=mode)
        except NonExistentCourseError:
            raise NotFound(detail=u"No course '{}' found".format(course_id))
        except CourseEnrollmentException as e:
            return RESTResponse({'detail': e.message or u"Enrollment failed ({})".format(e.__class__.__name__)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.info("SEND_ENROLLMENT_EMAIL")
            # if settings.FEATURES.get('SEND_ENROLLMENT_EMAIL') and not skip_enrollment_email:
            #     # course is already checked for existence
            #     course = CourseOverview.get_from_id(course_id)
            #     send_enrollment_email(user, course, use_https_for_links=request.is_secure())
        serializer = CourseEnrollmentSerializer(enrollment)
        return RESTResponse(serializer.data)

    @detail_route(methods=['post'])
    def unenroll(self, request, *args, **kwargs):
        user = self._get_user(*args, **kwargs)
        course_id = self.kwargs.get(self.lookup_field, None)
        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            raise NotFound(detail=_("No course '{}' found").format(course_id))

        if not CourseEnrollment.is_enrolled(user, course_key):
            try:
                course = CourseOverview.get_from_id(course_key)
            except CourseOverview.DoesNotExist:
                raise NotFound(detail=u"No course '{}' found".format(course_id))
            else:
                return RESTResponse({'detail': u"User is not enrolled in this course"},
                                status=status.HTTP_400_BAD_REQUEST)

        CourseEnrollment.unenroll(user, course_key)
        return RESTResponse(status=status.HTTP_204_NO_CONTENT)

    def _get_enrollments(self, *args, **kwargs):
        user = self._get_user(*args, **kwargs)
        return [enrollment for enrollment in CourseEnrollment.enrollments_for_user(user)
                if not isinstance(modulestore().get_course(enrollment.course_id), ErrorDescriptor)]

    def _get_user(self, *args, **kwargs):
        username = self.kwargs['user_username']
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound(detail=u"No user with uid '{}' found".format(username))
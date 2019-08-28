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
from rest_framework.response import Response as RESTResponse, Response
from enrollment import api
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from itoo_api.models import Program, OrganizationCustom
from itoo_api.serializers import ProgramSerializer, OrganizationSerializer, ProgramCourseSerializer, \
    OrganizationCustomSerializer, OrganizationCourseSerializer, CourseModeSerializer

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

# acquiring

class PaidCoursesViewSet(APIView):

    def get(self, request, course_id=None):
        course_key = CourseKey.from_string(course_id)
        course = get_course_by_id(course_key)
        return RESTResponse({"course": str(course)})


class PaidCoursesCusViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = CourseOverview.objects.all() # pylint: disable=no-member
    serializer_class = CourseModeSerializer
    lookup_field = 'id'


@api_view()
def add_enroll(self, request, course_id=None, user_id=None):
    username = user_id or request.user.username
    mode = "verified"
    logger.warning(user_id)
    api.add_enrollment(username, course_id, mode)
    return Response({"message": "Hello, world!"})
# pylint: disable=too-many-ancestors
"""
Views for itoo_api end points.
"""
import logging
# from organizations.models import Organization
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from itoo_api.models import Program, OrganizationCustom, EduProject, EnrollProgram
from itoo_api.serializers import ProgramSerializer, ProgramCourseSerializer, \
    OrganizationCustomSerializer, OrganizationCourseSerializer, EduProjectSerializer, EnrollProgramSerializer

from itoo_api.verified_profile.models import Profile
from itoo_api.serializers import ProfileSerializer
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

# from student.views import send_enrollment_email
logging.basicConfig()
logger = logging.getLogger(__name__)


class EduProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """ view to fetch list programs data or single program
    using program short name.
    """
    queryset = EduProject.objects.filter(active=True)  # pylint: disable=no-member
    serializer_class = EduProjectSerializer
    lookup_field = 'slug'


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ view to fetch list programs data or single program
    using program short name.
    """
    queryset = Profile.objects.all()  # pylint: disable=no-member
    serializer_class = ProfileSerializer
    lookup_field = 'user__username'


# class MultipleFieldLookupMixin(object):
#     """
#     Apply this mixin to any view or viewset to get multiple field filtering
#     based on a `lookup_fields` attribute, instead of the default single field filtering.
#     """
#
#     def get_object(self, *args, **kwargs):
#         logger.warning(self.kwargs)
#         user = self.kwargs["pk"].split(",")[0]
#         program = self.kwargs["pk"].split(",")[1]
#         obj = EnrollProgram.objects.filter(user=user,program=program)
#         # queryset = self.get_queryset()  # Get the base queryset
#         # queryset = self.filter_queryset(queryset)  # Apply any filter backends
#         # filter = {}
#
#         #
#         # for field in self.lookup_fields:
#         #
#         #     if self.kwargs[field]:  # Ignore empty fields.
#         #         filter[field] = self.kwargs[field]
#         # obj = get_object_or_404(queryset, **filter)  # Lookup the object
#
#
#         return obj
from django.db.models import Q
import operator


# class MultipleFieldLookupMixin(object):
#     """
#     Apply this mixin to any view or viewset to get multiple field filtering
#     based on a `lookup_fields` attribute, instead of the default single field filtering.
#     """
#
#     def get_object(self):
#         queryset = self.get_queryset()  # Get the base queryset
#         queryset = self.filter_queryset(queryset)  # Apply any filter backends
#         filter = {}
#         for field in self.lookup_fields:
#             if self.kwargs[field]:  # Ignore empty fields.
#                 filter[field] = self.kwargs[field]
#         obj = get_object_or_404(queryset, **filter)  # Lookup the object
#         self.check_object_permissions(self.request, obj)
#         return obj


class EnrollProgramViewSet(APIView):
    """Program view to fetch list programs data or single program
    using program short name.
    """

    queryset = EnrollProgram.objects.all()  # pylint: disable=no-member
    serializer_class = EnrollProgramSerializer

    def get(self, request, username=None, program_slug=None):
        """Create, read, or update enrollment information for a user.
        HTTP Endpoint for all CRUD operations for a user course enrollment. Allows creation, reading, and
        updates of the current enrollment for a particular course.
        Args:
            request (Request): To get current course enrollment information, a GET request will return
                information for the current user and the specified course.
            course_id (str): URI element specifying the course location. Enrollment information will be
                returned, created, or updated for this particular course.
            username (str): The username associated with this enrollment request.
        Return:
            A JSON serialized representation of the course enrollment.
        """
        username = username or request.user.username

        uid = User.objects.get(username=username)

        # TODO Implement proper permissions
        if request.user.username != username and not request.user.is_superuser:
            # Return a 404 instead of a 403 (Unauthorized). If one user is looking up
            # other users, do not let them deduce the existence of an enrollment.
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            program = Program.get_program(slug=program_slug)
            if program:
                try:
                    enroll_program = EnrollProgram.get_enroll_program(user=request.user, program=program)
                    return Response(EnrollProgramSerializer(enroll_program).data)
                except ObjectDoesNotExist:
                    return None

        except:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "message": (
                        u"An error occurred while retrieving enrollments for user "
                        u"'{username}' in course '{course_id}'"
                    ).format(user=request.user.username, program_slug=program_slug)
                }
            )


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

# class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
#     """Program view to fetch list programs data or single program
#     using program short name.
#     """
#     queryset = Organization.objects.filter(active=True)  # pylint: disable=no-member
#     serializer_class = OrganizationSerializer
#     lookup_field = 'short_name'

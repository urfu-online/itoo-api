# pylint: disable=too-many-ancestors
"""
Views for itoo_api end points.
"""
import logging
# from organizations.models import Organization
from rest_framework import viewsets
from django.shortcuts import get_object_or_404

from itoo_api.models import Program, OrganizationCustom, EduProject, EnrollProgram
from itoo_api.serializers import ProgramSerializer, ProgramCourseSerializer, \
    OrganizationCustomSerializer, OrganizationCourseSerializer, EduProjectSerializer, EnrollProgramSerializer

from itoo_api.verified_profile.models import Profile
from itoo_api.serializers import ProfileSerializer

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


class MultipleFieldLookupMixin(object):
    """
    Apply this mixin to any view or viewset to get multiple field filtering
    based on a `lookup_fields` attribute, instead of the default single field filtering.
    """

    def get_object(self):
        queryset = self.get_queryset()  # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs[field]:  # Ignore empty fields.
                filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)  # Lookup the object
        logger.warning(obj)
        return obj


class EnrollProgramViewSet(MultipleFieldLookupMixin, viewsets.ReadOnlyModelViewSet):
    """Program view to fetch list programs data or single program
    using program short name.
    """
    queryset = EnrollProgram.objects.all()  # pylint: disable=no-member
    serializer_class = EnrollProgramSerializer
    lookup_field = ('user__username', 'program_slug')


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

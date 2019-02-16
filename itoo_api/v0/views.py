# pylint: disable=too-many-ancestors
"""
Views for itoo_api end points.
"""
from organizations.models import Organization
from rest_framework import viewsets

from itoo_api.models import Program, ProgramCourse
from itoo_api.serializers import ProgramSerializer, OrganizationSerializer, ProgramCourseSerializer


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
    lookup_field = 'id'


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """Program view to fetch list programs data or single program
    using program short name.
    """
    queryset = Organization.objects.filter(active=True)  # pylint: disable=no-member
    serializer_class = OrganizationSerializer
    lookup_field = 'short_name'

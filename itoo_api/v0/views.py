# pylint: disable=too-many-ancestors
"""
Views for organizations end points.
"""
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_oauth.authentication import OAuth2Authentication

from organizations.models import Program
from organizations.serializers import ProgramSerializer


class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    """Program view to fetch list programs data or single program
    using program short name.
    """
    queryset = Program.objects.filter(active=True)  # pylint: disable=no-member
    serializer_class = ProgramSerializer
    lookup_field = 'short_name'
    # authentication_classes = (OAuth2Authentication, JwtAuthentication, SessionAuthentication)
    # permission_classes = (IsAuthenticated,)

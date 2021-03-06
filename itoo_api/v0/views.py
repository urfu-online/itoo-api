# pylint: disable=too-many-ancestors
"""
Views for itoo_api end points.
"""
import logging
# from organizations.models import Organization
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
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
from importlib import import_module
from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend
import json
logging.basicConfig()
logger = logging.getLogger(__name__)


class CheckSessionID(APIView):

    def post(self, request):
        my_key = request.COOKIES.get('sessionid', None)
        engine = import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore(my_key)

        try:
            user_id = session[SESSION_KEY]
            backend_path = session[BACKEND_SESSION_KEY]
            backend = load_backend(backend_path)
            user = backend.get_user(user_id) or AnonymousUser()
        except KeyError:
            user = AnonymousUser()

        if user.is_authenticated():
            return Response({'detail': True})
        else:
            return Response({'detail': False})


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


class EnrollProgramViewSet(viewsets.ModelViewSet):
    """Program view to fetch list programs data or single program
    using program short name.
    """

    queryset = EnrollProgram.objects.all()  # pylint: disable=no-member
    serializer_class = EnrollProgramSerializer
    permission_classes = [AllowAny]
    lookup_url_kwarg = "program_slug"

    def retrieve(self, request, *args, **kwargs):
        username = request.user.username
        program_slug = self.kwargs.get(self.lookup_url_kwarg)
        # uid = User.objects.get(username=username)

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
                    if enroll_program:
                        return Response(EnrollProgramSerializer(enroll_program).data)
                    else:
                        return Response({'detail': 'failed'})
                except ObjectDoesNotExist:
                    return Response({'detail': 'failed'})
            else:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "message": (
                            u"An error occurred while retrieving enrollments for user "
                            u"'{user}' in course '{program_slug}'"
                        ).format(user=request.user.username, program_slug=program_slug)
                    }
                )

        except:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "message": (
                        u"An error occurred while retrieving enrollments for user "
                        u"'{user}' in course '{program_slug}'"
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

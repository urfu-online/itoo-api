"""
Data layer serialization operations.  Converts querysets to simple
python containers (mainly arrays and dicts).
"""
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from organizations.models import Organization
from rest_framework import serializers

from itoo_api.models import Program, ProgramCourse


class CourseSerializer(serializers.ModelSerializer):  # pylint: disable=abstract-method
    """
    Serialize a course descriptor and related information.
    """
    class Meta:
        model = CourseOverview
        fields = ('start_display', )

    # course_id = serializers.CharField(source="id")
    # course_name = serializers.CharField(source="display_name_with_default")
    # enrollment_start = serializers.DateTimeField(format=None)
    # enrollment_end = serializers.DateTimeField(format=None)
    # course_start = serializers.DateTimeField(source="start", format=None)
    # course_end = serializers.DateTimeField(source="end", format=None)
    # invite_only = serializers.BooleanField(source="invitation_only")
    #
    # def __init__(self, *args, **kwargs):
    #     self.include_expired = kwargs.pop("include_expired", False)
    #     super(CourseSerializer, self).__init__(*args, **kwargs)


# pylint: disable=too-few-public-methods
class ProgramSerializer(serializers.ModelSerializer):
    """ Serializes the Program object."""

    class Meta(object):  # pylint: disable=missing-docstring
        model = Program
        fields = ('id', 'name', 'short_name', 'description', 'logo', 'active')


class ProgramCourseSerializer(serializers.ModelSerializer):
    """ Serializes the Program object."""
    course = serializers.SerializerMethodField()

    class Meta(object):  # pylint: disable=missing-docstring
        model = ProgramCourse
        fields = ('course', 'program', 'active')

    def get_course(self, obj):
        course_key = CourseKey.from_string(obj.course_id)
        course = CourseOverview.get_from_id(course_key)
        return CourseSerializer(course).data


class OrganizationSerializer(serializers.ModelSerializer):
    """ Serializes the Organization object."""

    class Meta(object):  # pylint: disable=missing-docstring
        model = Organization
        fields = ('id', 'name', 'short_name', 'description', 'logo', 'active')


def serialize_program(program):
    """
    Program object-to-dict serialization
    """
    return {
        'id': program.id,
        'name': program.name,
        'short_name': program.short_name,
        'description': program.description,
        'logo': program.logo,
    }


def serialize_programs(programs):
    """
    Program serialization
    Converts list of objects to list of dicts
    """
    return [serialize_program(program) for program in programs]

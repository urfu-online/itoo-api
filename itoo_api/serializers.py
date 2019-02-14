"""
Data layer serialization operations.  Converts querysets to simple
python containers (mainly arrays and dicts).
"""
from course_api.serializers import CourseSerializer
from courseware.courses import get_course_by_id
from organizations.models import Organization
from rest_framework import serializers

from itoo_api.models import Program, ProgramCourse


# pylint: disable=too-few-public-methods
class ProgramSerializer(serializers.ModelSerializer):
    """ Serializes the Program object."""

    class Meta(object):  # pylint: disable=missing-docstring
        model = Program
        fields = ('id', 'name', 'short_name', 'description', 'logo', 'active')


class ProgramCourseSerializer(serializers.ModelSerializer):
    """ Serializes the Program object."""
    course = serializers.SerializerMethodField()

    def get_course(self, obj):
        course = get_course_by_id(obj.course.id)
        return course

    class Meta(object):  # pylint: disable=missing-docstring
        model = ProgramCourse
        fields = ('course', 'program', 'active')


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

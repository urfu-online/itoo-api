"""
Data layer serialization operations.  Converts querysets to simple
python containers (mainly arrays and dicts).
"""
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from organizations.models import Organization
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from student.models import CourseEnrollment
from django.contrib.auth.models import User

from itoo_api.models import Program, ProgramCourse, OrganizationCustom, OrganizationCourse


class CourseSerializer(serializers.ModelSerializer):  # pylint: disable=abstract-method
    """
    Serialize a course descriptor and related information.
    """
    class Meta:
        model = CourseOverview
        fields = ('id','display_name','course_image_url','start_display','catalog_visibility')


# pylint: disable=too-few-public-methods
class ProgramSerializer(serializers.ModelSerializer):
    """ Serializes the Program object."""

    class Meta(object):  # pylint: disable=missing-docstring
        model = Program
        fields = ('id', 'name', 'short_name', 'slug', 'description', 'logo', 'active')


class ProgramCourseSerializer(serializers.ModelSerializer):
    """ Serializes the Program object."""
    course = serializers.SerializerMethodField()
    program_slug = serializers.CharField(source='program.slug')

    class Meta(object):  # pylint: disable=missing-docstring
        model = ProgramCourse
        fields = ('course', 'program_slug', 'active','course_id')

    def get_course(self, obj):
        course_key = CourseKey.from_string(obj.course_id)
        course = CourseOverview.get_from_id(course_key)
        return CourseSerializer(course).data


class OrganizationCustomSerializer(serializers.ModelSerializer):
    """ Serializes the OrganizationCustom object."""

    class Meta(object):  # pylint: disable=missing-docstring
        model = OrganizationCustom
        fields = ('id', 'name', 'short_name', 'slug', 'description', 'logo', 'active')


class OrganizationCourseSerializer(serializers.ModelSerializer):
    """ Serializes the OrganizationCustom object."""
    course = serializers.SerializerMethodField()
    org_slug = serializers.CharField(source='org.slug')

    class Meta(object):  # pylint: disable=missing-docstring
        model = OrganizationCourse
        fields = ('course', 'org_slug', 'active','course_id')

    def get_course(self, obj):
        course_key = CourseKey.from_string(obj.course_id)
        course = CourseOverview.get_from_id(course_key)
        return CourseSerializer(course).data


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializes enrollment information for course summary
    """
    uid = serializers.CharField(source='username', required=True, allow_blank=False, validators=[UniqueValidator(queryset=User.objects)])

    class Meta:
        model = CourseEnrollment
        fields = ('uid', 'mode', 'is_active', 'created')


class UserEnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializes enrollment information for user dashboard
    """
    grade = serializers.SerializerMethodField()
    certificate_url = serializers.SerializerMethodField()

    class Meta:
        model = CourseEnrollment
        fields = ('course_id', 'mode', 'grade')


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

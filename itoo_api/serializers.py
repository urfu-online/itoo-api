"""
Data layer serialization operations.  Converts querysets to simple
python containers (mainly arrays and dicts).
"""
import logging
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
# from organizations.models import Organization
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from student.models import CourseEnrollment
from django.contrib.auth.models import User

from itoo_api.models import Program, OrganizationCustom, EduProject, TextBlock, EnrollProgram
from itoo_api.verified_profile.models import Profile

logging.basicConfig()
logger = logging.getLogger(__name__)


class CourseSerializerCatalog(serializers.ModelSerializer):  # pylint: disable=abstract-method
    """
    Serialize a course descriptor and related information.
    """

    class Meta:
        model = CourseOverview
        fields = (
            'id', 'display_name', 'course_image_url', 'start_display', 'catalog_visibility',
            'org')  # description field ????


class TextBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextBlock
        fields = ('type_slug', 'content')


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = Profile
        fields = ('username', 'email', 'all_valid')


class EnrollProgramSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    program_slug = serializers.CharField(source='program.slug')

    class Meta:
        model = EnrollProgram
        fields = ('username', 'email', 'program_slug')


# class TextBlockRelatedField(serializers.RelatedField):
#     def to_representation(self, value):
#         """
#         Serialize bookmark instances using a bookmark serializer,
#         and note instances using a note serializer.
#         """
#         print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', value)
#         serializer = TextBlockSerializer(value)
#
#         return serializer.data


# pylint: disable=too-few-public-methods
class ProgramSerializer(serializers.ModelSerializer):
    """ Serializes the Program object."""
    project_slug = serializers.CharField(source='project.slug')
    owner_slug = serializers.CharField(source='owner.slug')
    content = serializers.SerializerMethodField()
    direction = serializers.CharField(source='direction.title')
    edu_start_date = serializers.DateField(format="%d.%m.%Y")
    edu_end_date = serializers.DateField(format="%d.%m.%Y")

    class Meta:  # pylint: disable=missing-docstring
        model = Program
        fields = (
            'id', 'title', 'owner_slug', 'project_slug', 'short_name', 'slug', 'description', 'logo',
            'image_background',
            'active', 'content', 'id_unit_program', 'edu_start_date', 'edu_end_date', 'number_of_hours',
            'issued_document_name', 'direction', 'enrollment_allowed')

    def get_content(self, obj):
        content_serializer = TextBlockSerializer(obj.content(), many=True)
        return content_serializer.data


class ProgramForProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ('slug',)


# pylint: disable=too-few-public-methods
class EduProjectSerializer(serializers.ModelSerializer):
    """ Serializes the Program object."""
    owner_slug = serializers.CharField(source='owner.slug')
    program = ProgramForProjectSerializer(many=True, read_only=True, source='realized_programs')
    # program = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:  # pylint: disable=missing-docstring
        model = EduProject
        fields = (
            'id', 'title', 'owner_slug', 'short_name', 'slug', 'description', 'logo', 'image_background', 'active',
            'content', 'program')

    # def get_program(self, obj):
    #     program_serializer = ProgramForProjectSerializer(obj.content(), many=True)
    #     return program_serializer.data

    def get_content(self, obj):
        content_serializer = TextBlockSerializer(obj.content(), many=True)
        return content_serializer.data


class ProgramCourseSerializer(serializers.ModelSerializer):
    """ Serializes the Program object."""
    courses = serializers.SerializerMethodField()

    # program_slug = serializers.CharField(source='program.slug')

    class Meta(object):  # pylint: disable=missing-docstring
        model = Program
        fields = ('title', 'slug', 'active', 'courses')

    def get_courses(self, obj):
        course_keys = [CourseKey.from_string(course.course_id) for course in obj.get_courses()]
        courses = [CourseOverview.get_from_id(course_key) for course_key in course_keys]
        return CourseSerializerCatalog(courses, many=True).data


class OrganizationCustomSerializer(serializers.ModelSerializer):
    """ Serializes the OrganizationCustom object."""

    class Meta(object):  # pylint: disable=missing-docstring
        model = OrganizationCustom
        fields = ('id', 'title', 'short_name', 'slug', 'description', 'logo', 'image_background', 'active')


class OrganizationCourseSerializer(serializers.ModelSerializer):
    """ Serializes the OrganizationCustom object."""
    courses = serializers.SerializerMethodField()

    # org_slug = serializers.CharField(source='org.slug')

    class Meta(object):  # pylint: disable=missing-docstring
        model = OrganizationCustom
        fields = ('title', 'slug', 'active', 'courses')

    def get_courses(self, obj):
        course_keys = [CourseKey.from_string(course.course_id) for course in obj.get_courses()]
        courses = [CourseOverview.get_from_id(course_key) for course_key in course_keys]
        return CourseSerializerCatalog(courses, many=True).data


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializes enrollment information for course summary
    """
    uid = serializers.CharField(source='username', required=True, allow_blank=False,
                                validators=[UniqueValidator(queryset=User.objects)])

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


# class OrganizationSerializer(serializers.ModelSerializer):
#     """ Serializes the Organization object."""
#
#     class Meta(object):  # pylint: disable=missing-docstring
#         model = Organization
#         fields = ('id', 'name', 'short_name', 'description', 'logo', 'active')


def serialize_program(program):
    """
    Program object-to-dict serialization
    """
    return {
        'id': program.id,
        'title': program.title,
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

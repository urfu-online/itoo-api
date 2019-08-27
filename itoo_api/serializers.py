"""
Data layer serialization operations.  Converts querysets to simple
python containers (mainly arrays and dicts).
"""
import logging
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from course_modes.models import CourseMode
from organizations.models import Organization
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from student.models import CourseEnrollment
from django.contrib.auth.models import User

from itoo_api.models import Program, ProgramCourse, OrganizationCustom, OrganizationCourse

logging.basicConfig()
logger = logging.getLogger(__name__)


class CourseSerializerCatalog(serializers.ModelSerializer):  # pylint: disable=abstract-method
    """
    Serialize a course descriptor and related information.
    """
    class Meta:
        model = CourseOverview
        fields = ('id','display_name','course_image_url','start_display','catalog_visibility') # description field ????


# pylint: disable=too-few-public-methods
class ProgramSerializer(serializers.ModelSerializer):
    """ Serializes the Program object."""

    class Meta(object):  # pylint: disable=missing-docstring
        model = Program
        fields = ('id', 'name', 'short_name', 'slug', 'description', 'logo', 'image_background', 'active')


class ProgramCourseSerializer(serializers.ModelSerializer):
    """ Serializes the Program object."""
    courses = serializers.SerializerMethodField()
    # program_slug = serializers.CharField(source='program.slug')

    class Meta(object):  # pylint: disable=missing-docstring
        model = Program
        fields = ('name', 'slug', 'active', 'courses')

    def get_courses(self, obj):
        course_keys = [CourseKey.from_string(course.course_id) for course in obj.get_courses()]
        courses = [CourseOverview.get_from_id(course_key) for course_key in course_keys]
        return CourseSerializerCatalog(courses, many=True).data


class OrganizationCustomSerializer(serializers.ModelSerializer):
    """ Serializes the OrganizationCustom object."""

    class Meta(object):  # pylint: disable=missing-docstring
        model = OrganizationCustom
        fields = ('id', 'name', 'short_name', 'slug', 'description', 'logo', 'image_background', 'active')


class OrganizationCourseSerializer(serializers.ModelSerializer):
    """ Serializes the OrganizationCustom object."""
    courses = serializers.SerializerMethodField()
    # org_slug = serializers.CharField(source='org.slug')

    class Meta(object):  # pylint: disable=missing-docstring
        model = OrganizationCustom
        fields = ('name', 'slug', 'active','courses')

    def get_courses(self, obj):
        course_keys = [CourseKey.from_string(course.course_id) for course in obj.get_courses()]
        courses = [CourseOverview.get_from_id(course_key) for course_key in course_keys]
        return CourseSerializerCatalog(courses, many=True).data


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


class CourseModeSerializer(serializers.ModelSerializer):
    """ Serializes the CourseMode object."""

    # courses = serializers.SerializerMethodField()
    course_modes = serializers.SerializerMethodField()
    # program_slug = serializers.CharField(source='program.slug')
    course_id = serializers.CharField(source="id")
    course_name = serializers.CharField(source="display_name_with_default")

    class Meta:
        model = CourseOverview
        fields = ('course_id','course_name','course_modes')

    # def get_courses(self, obj):
    #     course_keys = [CourseKey.from_string(course.course_id) for course in obj.get_courses()]
    #     # courses = [CourseOverview.get_from_id(course_key) for course_key in course_keys]
    #     # qs = CourseMode.objects.filter(mode_slug="verified")
    #     course_modes = [CourseMode.modes_for_course(course_key, only_selectable=False) for course_key in course_keys]
    #     return ModeSerializer(course_modes, many=True).data

    def get_course_modes(self, obj):
        logger.warrning(obj.id)
        logger.warrning("!!!!!!!!!!!!!!!!!!!!!!1111111")
        course_modes = CourseMode.modes_for_course(
            obj.id,
            only_selectable=False
        )
        return [
            ModeSerializer(mode).data
            for mode in course_modes
        ]


class StringListField(serializers.CharField):
    """Custom Serializer for turning a comma delimited string into a list.
    This field is designed to take a string such as "1,2,3" and turn it into an actual list
    [1,2,3]
    """
    def field_to_native(self, obj, field_name):
        """
        Serialize the object's class name.
        """
        if not obj.suggested_prices:
            return []

        items = obj.suggested_prices.split(',')
        return [int(item) for item in items]


class ModeSerializer(serializers.Serializer):
    """Serializes a course's 'Mode' tuples
    Returns a serialized representation of the modes available for course enrollment. The course
    modes models are designed to return a tuple instead of the model object itself. This serializer
    does not handle the model object itself, but the tuple.
    """
    slug = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=255)
    min_price = serializers.IntegerField()
    suggested_prices = StringListField(max_length=255)
    currency = serializers.CharField(max_length=8)
    expiration_datetime = serializers.DateTimeField()
    description = serializers.CharField()
    sku = serializers.CharField()
    bulk_sku = serializers.CharField()

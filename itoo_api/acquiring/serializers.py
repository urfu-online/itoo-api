import logging

# from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from course_modes.models import CourseMode
from rest_framework import serializers
# from enrollment import api

logging.basicConfig()
logger = logging.getLogger(__name__)





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


class TestdataSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    course_key = serializers.CharField(max_length=2048)
    mode = serializers.CharField(max_length=255)
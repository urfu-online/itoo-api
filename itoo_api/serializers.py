"""
Data layer serialization operations.  Converts querysets to simple
python containers (mainly arrays and dicts).
"""
from rest_framework import serializers

from itoo_api.models import Program
from organizations.models import Organization


# pylint: disable=too-few-public-methods
class ProgramSerializer(serializers.ModelSerializer):
    """ Serializes the Program object."""
    class Meta(object):  # pylint: disable=missing-docstring
        model = Program
        fields = ('id', 'name', 'short_name', 'description', 'logo', 'active')


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
        'logo': program.logo
    }


def serialize_programs(programs):
    """
    Program serialization
    Converts list of objects to list of dicts
    """
    return [serialize_program(program) for program in programs]

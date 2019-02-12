"""
Data layer serialization operations.  Converts querysets to simple
python containers (mainly arrays and dicts).
"""
from rest_framework import serializers

from itoo_api import models
from organizations import models1


# pylint: disable=too-few-public-methods
class ProgramSerializer(serializers.ModelSerializer):
    """ Serializes the Program object."""
    class Meta(object):  # pylint: disable=missing-docstring
        model = models.Program
        fields = ('id', 'name', 'short_name', 'description', 'logo')


class OrganizationSerializer(serializers.ModelSerializer):
    """ Serializes the Organization object."""
    class Meta(object):  # pylint: disable=missing-docstring
        model = models1.Organization
        fields = '__all__'


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

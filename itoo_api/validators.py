# This Python file uses the following encoding: utf-8
"""
Validators confirm the integrity of inbound information prior to a data.py handoff
"""
from six import text_type
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey


def course_key_is_valid(course_key):
    """
    Course key object validation
    """
    if course_key is None:
        return False
    try:
        CourseKey.from_string(text_type(course_key))
    except (InvalidKeyError, UnicodeDecodeError):
        return False
    return True


def program_data_is_valid(program_data):
    """
    Program data validation
    """
    if program_data is None:
        return False
    if 'id' in program_data and not program_data.get('id'):
        return False
    if 'name' in program_data and not program_data.get('name'):
        return False
    return True

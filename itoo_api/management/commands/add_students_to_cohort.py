from django.core.management.base import BaseCommand
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.course_groups.cohorts import (
    add_user_to_cohort,
    remove_user_from_cohort,
    is_cohort_exists,
    add_cohort,
    bulk_cache_cohorts,
)
from student.models import CourseEnrollment
import codecs
import logging
import os
from django.utils.translation import ugettext as _

DEFAULT_COHORT_NAME = _("Default Group")
# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Moves students with the @urfu.me email domain from one cohort to another."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--course_ids",
            nargs="+",
            help="List of course_id (e.g., course-v1:YourOrg+Course1+Run1)."
        )
        group.add_argument(
            "--file",
            type=str,
            help="Path to a file containing a list of course_id (one per line)."
        )
        parser.add_argument(
            "--source_cohort_name",
            type=str,
            required=True,
            default=DEFAULT_COHORT_NAME,
            help="Name of the source cohort (e.g., 'OldCohort')."
        )
        parser.add_argument(
            "--target_cohort_name",
            type=str,
            required=True,
            help="Name of the target cohort (e.g., 'Stud')."
        )
        parser.add_argument(
            "--email_domain",
            type=str,
            default="@urfu.me",
            help="Email domain to filter students (default: '@urfu.me')."
        )

    def handle(self, *args, **options):
        course_ids = []
        source_cohort_name = options["source_cohort_name"]
        target_cohort_name = options["target_cohort_name"]
        email_domain = options["email_domain"]

        # Get the list of course_ids
        if options["course_ids"]:
            course_ids = options["course_ids"]
        elif options["file"]:
            if not os.path.exists(options["file"]):
                logger.error("File {} not found.".format(options["file"]))
                return
            try:
                with codecs.open(options["file"], "r", encoding="utf-8") as f:
                    course_ids = [line.strip() for line in f if line.strip()]
            except (IOError, OSError) as e:
                logger.error("Error reading file {}: {}".format(options["file"], str(e)))
                return

        if not course_ids:
            logger.error("Course ID list is empty. Please provide course_ids or a valid file.")
            return

        for course_id_str in course_ids:
            try:
                course_key = CourseKey.from_string(course_id_str)
            except Exception as e:
                logger.error("Error processing course_id '{}': {}".format(course_id_str, str(e)))
                continue

            logger.info("Processing course: {}".format(course_id_str))

            # Check if source and target cohorts exist
            try:
                source_cohort = get_cohort_by_name(course_key, source_cohort_name)
                if not is_cohort_exists(course_key, target_cohort_name):
                    add_cohort(course_key, target_cohort_name, assignment_type="manual")
                    logger.info("Created new cohort '{}' for course {}.".format(target_cohort_name, course_id_str))
                target_cohort = get_cohort_by_name(course_key, target_cohort_name)
            except Exception as e:
                logger.error("Error working with cohorts: {}".format(str(e)))
                continue

            # Find all active students in the course
            enrollments = CourseEnrollment.objects.filter(course_id=course_key, is_active=True)
            students = [enrollment.user for enrollment in enrollments]

            # Cache cohort data for students
            bulk_cache_cohorts(course_key, students)

            # Filter students in the source cohort
            students_in_source_cohort = [
                student for student in students
                if student.email.endswith(email_domain) and get_cohort(student, course_key) == source_cohort
            ]
            logger.info("Found {} students with domain {} in cohort '{}'.".format(
                len(students_in_source_cohort), email_domain, source_cohort_name
            ))

            # Move students from the source cohort to the target cohort
            for student in students_in_source_cohort:
                try:
                    remove_user_from_cohort(source_cohort, student.username)
                    add_user_to_cohort(target_cohort, student)
                    logger.info("Moved student {} from cohort '{}' to cohort '{}'.".format(
                        student.username, source_cohort_name, target_cohort_name
                    ))
                except Exception as e:
                    logger.error("Failed to move student {}: {}".format(student.username, str(e)))

        logger.info("Process completed.")

def get_cohort(user, course_key):
    """
    Returns the cohort to which the user belongs.
    """
    from openedx.core.djangoapps.course_groups.cohorts import get_cohort as get_cohort_func
    return get_cohort_func(user, course_key, assign=False, use_cached=True)

def get_cohort_by_name(course_key, name):
    """
    Returns the cohort object by name.
    """
    from openedx.core.djangoapps.course_groups.models import CourseUserGroup
    return CourseUserGroup.objects.get(
        course_id=course_key,
        group_type=CourseUserGroup.COHORT,
        name=name
    )
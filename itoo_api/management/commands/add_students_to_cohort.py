from django.core.management.base import BaseCommand
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.course_groups.cohorts import (
    add_user_to_cohort,
    remove_user_from_cohort,
    is_cohort_exists,
    add_cohort,
    bulk_cache_cohorts,
    set_course_cohorted,
)
from student.models import CourseEnrollment
import codecs
import logging
import os
from social_django.models import UserSocialAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Moves students with the @urfu.me email domain from any cohort to the target cohort."

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
        parser.add_argument(
            "--provider",
            type=str,
            default="keycloak",
            help="Идентификатор стороннего провайдера аутентификации (например, 'keycloak')."
        )

    def handle(self, *args, **options):
        course_ids = []
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

            # Ensure cohorts are enabled for the course
            try:
                set_course_cohorted(course_key, cohorted=True)
                logger.info("Enabled cohorts for course {}.".format(course_id_str))
            except ValueError as e:
                logger.error("Failed to enable cohorts for course {}: {}".format(course_id_str, str(e)))
                continue

            # Check if the target cohort exists
            try:
                if not is_cohort_exists(course_key, target_cohort_name):
                    add_cohort(course_key, target_cohort_name, assignment_type="manual")
                    logger.info("Created cohort '{}' for course {}.".format(target_cohort_name, course_id_str))
                target_cohort = get_cohort_by_name(course_key, target_cohort_name)
            except Exception as e:
                logger.error("Error working with cohorts: {}".format(str(e)))
                continue

            # Find all active students in the course
            enrollments = CourseEnrollment.objects.filter(course_id=course_key, is_active=True)
            students = [enrollment.user for enrollment in enrollments]

            # Cache cohort data for students
            bulk_cache_cohorts(course_key, students)

            # Filter students by email domain
            provider = options["provider"]
            students_to_move = []
            for student in students:
                email_matches = student.email.endswith(email_domain)
                is_linked = UserSocialAuth.objects.filter(user=student, provider=provider).exists()
                if email_matches or is_linked:
                    students_to_move.append(student)

            logger.info("Found {} students with domain {} to move.".format(len(students_to_move), email_domain))

            # Move students to the target cohort
            for student in students_to_move:
                try:
                    current_cohort = get_cohort(student, course_key)
                    if current_cohort and (current_cohort.name == "Студенты УрФУ долг" or current_cohort.name == "Студенты УрФУ контрольный проект" or current_cohort.name == "Студенты УрФУ контрольный проект 2"):
                        logger.info("Skipping student {} as they are in the cohort .".format(student.username))
                        continue
                except Exception as e:
                    logger.error("Error checking cohort for student {}: {}".format(student.username, str(e)))
                    continue

                source_cohort = get_cohort(student, course_key)
                try:
                    if source_cohort:
                        remove_user_from_cohort(source_cohort, student.username)
                        logger.info("Removed student {} from cohort '{}'.".format(student.username, source_cohort.name))
                    add_user_to_cohort(target_cohort, student)
                    logger.info("Moved student {} to cohort '{}'.".format(student.username, target_cohort_name))
                except ValueError as e:
                    logger.error("ValueError moving student {}: {}".format(student.username, str(e)))
                except IntegrityError as e:
                    logger.error("IntegrityError moving student {}: {}".format(student.username, str(e)))

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
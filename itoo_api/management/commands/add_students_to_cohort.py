from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from openedx.core.djangoapps.course_groups.models import CourseUserGroup
from student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey
import codecs
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = u"Adds students with the @urfu.me email domain to a cohort."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--course_ids",
            nargs="+",
            help=u"List of course_id (e.g., course-v1:YourOrg+Course1+Run1)."
        )
        group.add_argument(
            "--file",
            type=str,
            help=u"Path to a file containing a list of course_id (one per line)."
        )
        parser.add_argument(
            "--cohort_name",
            type=str,
            default="Stud",
            help=u"Cohort name (default: 'Stud')."
        )
        parser.add_argument(
            "--email_domain",
            type=str,
            default="@urfu.me",
            help=u"Email domain to filter students (default: '@urfu.me')."
        )

    def handle(self, *args, **options):
        course_ids = []
        cohort_name = options["cohort_name"]
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
            enrollments = CourseEnrollment.objects.filter(course_id=course_key, is_active=True)
            students = [enrollment.user for enrollment in enrollments]
            logger.info("Found {} students for course {}.".format(len(students), course_id_str))

            filtered_students = [student for student in students if student.email.endswith(email_domain)]
            logger.info("Filtered {} students with domain {}.".format(len(filtered_students), email_domain))

            try:
                cohort = CourseUserGroup.objects.get(name=cohort_name, course_id=course_key)
            except CourseUserGroup.DoesNotExist:
                cohort = CourseUserGroup(name=cohort_name, course_id=course_key, group_type="cohort")
                cohort.save()
                logger.info("Created new cohort '{}' for course {}.".format(cohort_name, course_id_str))

            existing_students = set(cohort.users.values_list("id", flat=True))
            new_students = [student for student in filtered_students if student.id not in existing_students]

            if new_students:
                from openedx.core.djangoapps.course_groups.cohorts import add_user_to_cohort  # Используем API для управления когортами <button class="citation-flag" data-index="4">
                for student in new_students:
                    try:
                        add_user_to_cohort(cohort, student.username)
                        logger.info("Moved student {} to cohort '{}'.".format(student.username, cohort_name))
                    except Exception as e:
                        logger.error("Failed to move student {} to cohort '{}': {}".format(student.username, cohort_name, str(e)))
            else:
                logger.info("All students are already in the cohort '{}'.".format(cohort_name))

        logger.info("Process completed.")
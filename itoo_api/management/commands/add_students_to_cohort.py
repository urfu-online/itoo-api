from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from openedx.core.djangoapps.course_groups.models import CourseUserGroup
from student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey
import codecs
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = u"Добавляет студентов с email-доменом @urfu.me в когорту."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--course_ids",
            nargs="+",
            help=u"Список course_id курсов (например, course-v1:YourOrg+Course1+Run1)."
        )
        group.add_argument(
            "--file",
            type=str,
            help=u"Путь к файлу, содержащему список course_id (по одному на строку)."
        )
        parser.add_argument(
            "--cohort_name",
            type=str,
            default="Stud",
            help=u"Название когорты (по умолчанию 'Stud')."
        )
        parser.add_argument(
            "--email_domain",
            type=str,
            default="@urfu.me",
            help=u"Домен email для фильтрации студентов (по умолчанию '@urfu.me')."
        )

    def handle(self, *args, **options):
        course_ids = []
        cohort_name = options["cohort_name"]
        email_domain = options["email_domain"]

        # Получаем список course_ids
        if options["course_ids"]:
            course_ids = options["course_ids"]
        elif options["file"]:
            if not os.path.exists(options["file"]):
                logger.error(u"Файл {} не найден.".format(options["file"]))
                return
            try:
                with codecs.open(options["file"], "r", encoding="utf-8") as f:
                    course_ids = [line.strip() for line in f if line.strip()]
            except (IOError, OSError) as e:
                logger.error(u"Ошибка при чтении файла {}: {}".format(options["file"], str(e)))
                return

        if not course_ids:
            logger.error(u"Список course_ids пуст. Пожалуйста, укажите course_ids или корректный файл.")
            return

        for course_id_str in course_ids:
            try:
                course_key = CourseKey.from_string(course_id_str)
            except Exception as e:
                logger.error(u"Ошибка при обработке course_id '{}': {}".format(course_id_str, str(e)))
                continue

            logger.info(u"Обработка курса: {}".format(course_id_str))

            enrollments = CourseEnrollment.objects.filter(course_id=course_key, is_active=True)
            students = [enrollment.user for enrollment in enrollments]

            logger.info(u"Найдено {} студентов для курса {}.".format(len(students), course_id_str))

            filtered_students = [student for student in students if student.email.endswith(email_domain)]
            logger.info(u"Отфильтровано {} студентов с доменом {}.".format(len(filtered_students), email_domain))

            cohort, created = CourseUserGroup.objects.get_or_create(name=cohort_name, course_id=course_key)

            if created:
                logger.info(u"Создана новая когорта '{}' для курса {}.".format(cohort_name, course_id_str))

            existing_students = set(cohort.users.values_list("id", flat=True))
            new_students = [student for student in filtered_students if student.id not in existing_students]

            if new_students:
                cohort.users.add(*new_students)
                logger.info(u"Добавлено {} студентов в когорту '{}'.".format(len(new_students), cohort_name))
            else:
                logger.info(u"Все студенты уже находятся в когорте '{}'.".format(cohort_name))

        logger.info(u"Завершено.")

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from openedx.core.djangoapps.course_groups.models import CourseUserGroup
from student.models import CourseEnrollment
import codecs

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
        cohort_name = options["cohort_name"].decode('utf-8')  # Декодируем в Unicode
        email_domain = options["email_domain"]

        # Нормализация имени когорты (убираем лишние пробелы)

        # Получаем список course_ids
        if options["course_ids"]:
            course_ids = [cid.decode('utf-8') for cid in options["course_ids"]]  # Декодируем в Unicode
        elif options["file"]:
            try:
                with codecs.open(options["file"], "r", encoding="utf-8") as f:
                    course_ids = [line.strip() for line in f if line.strip()]
            except IOError:
                self.stderr.write(u"Файл {} не найден.".format(options['file']))
                return

        if not course_ids:
            self.stderr.write(u"Список course_ids пуст. Пожалуйста, укажите course_ids или корректный файл.")
            return

        for course_id in course_ids:
            self.stdout.write(u"Обработка курса: {}".format(course_id))

            # Получаем список студентов, записанных на курс
            enrollments = CourseEnrollment.objects.filter(course_id=course_id, is_active=True)
            students = [enrollment.user for enrollment in enrollments]
            self.stdout.write(u"Найдено {} студентов для курса {}.".format(len(students), course_id))

            # Фильтруем студентов по домену email
            filtered_students = [student for student in students if student.email.endswith(email_domain)]
            self.stdout.write(u"Отфильтровано {} студентов с доменом {}.".format(len(filtered_students), email_domain))

            # Находим когорту по имени
            try:
                cohort = CourseUserGroup.objects.get(name=cohort_name, course_id=course_id)
            except CourseUserGroup.DoesNotExist:
                self.stderr.write(u"Когорта '{}' не найдена для курса {}. Пропускаем.".format(cohort_name, course_id))
                continue

            # Добавляем отфильтрованных студентов в когорту
            for student in filtered_students:
                if student not in cohort.users.all():
                    cohort.users.add(student)
                    self.stdout.write(u"Студент {} успешно добавлен в когорту '{}'.".format(student.username, cohort_name))
                else:
                    self.stdout.write(u"Студент {} уже состоит в когорте '{}'.".format(student.username, cohort_name))

        self.stdout.write(u"Завершено.")
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from openedx.core.djangoapps.course_groups.models import CourseUserGroup
from student.models import CourseEnrollment

class Command(BaseCommand):
    help = "Добавляет студентов с email-доменом @urfu.me в когорту Stud."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--course_ids",
            nargs="+",
            help="Список course_id курсов (например, course-v1:YourOrg+Course1+Run1)."
        )
        group.add_argument(
            "--file",
            type=str,
            help="Путь к файлу, содержащему список course_id (по одному на строку)."
        )
        parser.add_argument(
            "--cohort_name",
            type=str,
            default="Stud",
            help="Название когорты (по умолчанию 'Stud')."
        )
        parser.add_argument(
            "--email_domain",
            type=str,
            default="@urfu.me",
            help="Домен email для фильтрации студентов (по умолчанию '@urfu.me')."
        )

    def handle(self, *args, **options):
        course_ids = []
        cohort_name = options["cohort_name"]
        email_domain = options["email_domain"]

        # Получаем список course_ids
        if options["course_ids"]:
            course_ids = options["course_ids"]
        elif options["file"]:
            try:
                with open(options["file"], "r") as f:
                    course_ids = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                self.stderr.write(f"Файл {options['file']} не найден.")
                return

        if not course_ids:
            self.stderr.write("Список course_ids пуст. Пожалуйста, укажите course_ids или корректный файл.")
            return

        for course_id in course_ids:
            self.stdout.write(f"Обработка курса: {course_id}")

            # Получаем список студентов, записанных на курс
            enrollments = CourseEnrollment.objects.filter(course_id=course_id, is_active=True)
            students = [enrollment.user for enrollment in enrollments]
            self.stdout.write(f"Найдено {len(students)} студентов для курса {course_id}.")

            # Фильтруем студентов по домену email
            filtered_students = [student for student in students if student.email.endswith(email_domain)]
            self.stdout.write(f"Отфильтровано {len(filtered_students)} студентов с доменом {email_domain}.")

            # Находим когорту по имени
            try:
                cohort = CourseUserGroup.objects.get(name=cohort_name, course_id=course_id)
            except CourseUserGroup.DoesNotExist:
                self.stderr.write(f"Когорта {cohort_name} не найдена для курса {course_id}. Пропускаем.")
                continue

            # Добавляем отфильтрованных студентов в когорту
            for student in filtered_students:
                if student not in cohort.users.all():
                    cohort.users.add(student)
                    self.stdout.write(f"Студент {student.username} успешно добавлен в когорту {cohort_name}.")
                else:
                    self.stdout.write(f"Студент {student.username} уже состоит в когорте {cohort_name}.")

        self.stdout.write("Завершено.")
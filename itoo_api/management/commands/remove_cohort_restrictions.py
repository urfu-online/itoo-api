# auto_cohorting/management/commands/remove_cohort_restrictions.py
from django.core.management.base import BaseCommand
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.course_groups.models import CourseUserGroup
from xmodule.modulestore.django import modulestore
from collections import deque
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Удаляет когорты и снимает ограничения доступа к материалам курса."

    def add_arguments(self, parser):
        parser.add_argument(
            "--course_id",
            type=str,
            required=True,
            help="ID курса (например, course-v1:YourOrg+Course1+Run1)"
        )
        parser.add_argument(
            "--target_cohort",
            type=str,
            default="Студенты УрФУ",
            help="Имя целевой когорты"
        )
        parser.add_argument(
            "--forbidden_cohort",
            type=str,
            default="Студенты УрФУ долг",
            help="Имя запрещённой когорты"
        )

    def handle(self, *args, **options):
        course_id_str = options["course_id"]
        target_cohort_name = options["target_cohort"]
        forbidden_cohort_name = options["forbidden_cohort"]

        try:
            course_key = CourseKey.from_string(course_id_str)
        except Exception as e:
            logger.error(f"Ошибка парсинга course_id '{course_id_str}': {str(e)}")
            return

        # 1. Удаляем когорты
        self._delete_cohorts(course_key, target_cohort_name, forbidden_cohort_name)

        # 2. Получаем структуру курса
        store = modulestore()
        with store.bulk_operations(course_key):
            course = store.get_course(course_key, depth=3)
            if not course:
                logger.warning(f"Курс {course_id_str} не найден в Studio. Когорты удалены, материалы не обработаны.")
                return

            # 3. Находим первые 3 подраздела
            first_three_subs = self._get_first_n_subsections(course, n=3)

            # 4. Снимаем ограничения с остальных подразделов
            for section in course.get_children():
                for subsection in section.get_children():
                    if subsection not in first_three_subs:
                        self._remove_block_restrictions(subsection)

        logger.info("Откат завершён.")

    def _delete_cohorts(self, course_key, target_cohort_name, forbidden_cohort_name):
        """Удаляет указанные когорты, если они существуют."""
        from openedx.core.djangoapps.course_groups.cohorts import is_cohort_exists

        for name in [target_cohort_name, forbidden_cohort_name]:
            if is_cohort_exists(course_key, name):
                try:
                    cohort = CourseUserGroup.objects.get(
                        course_id=course_key,
                        group_type=CourseUserGroup.COHORT,
                        name=name
                    )
                    cohort.delete()
                    logger.info(f"Когорта '{name}' удалена из курса {course_key}")
                except Exception as e:
                    logger.error(f"Ошибка удаления когорты '{name}': {str(e)}")
            else:
                logger.info(f"Когорта '{name}' не найдена в курсе {course_key}. Пропуск.")

    def _get_first_n_subsections(self, course, n=3):
        """Возвращает первые N подразделов (независимо от разделов)."""
        result = []
        queue = deque(course.get_children())

        while queue and len(result) < n:
            node = queue.popleft()
            if node.category == "vertical":
                result.append(node)
            else:
                queue.extend(node.get_children())
        return result

    def _remove_block_restrictions(self, block):
        """Снимает ограничения доступа с указанного блока."""
        try:
            # Очищаем group_access и отключаем ограничения
            block.group_access = {
                "enabled": False,
                "cohorts": []
            }
            modulestore().update_item(block, ModuleStoreEnum.UserID.test)
            logger.info(f"Ограничения с блока {block.location} сняты")
        except Exception as e:
            logger.error(f"Ошибка снятия ограничений для блока {block.location}: {str(e)}")
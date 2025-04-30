# auto_cohorting/management/commands/setup_cohort_and_restrictions.py
from django.core.management.base import BaseCommand
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.course_groups.cohorts import (
    add_cohort,
    is_cohort_exists,
    set_course_cohorted,
)
from openedx.core.djangoapps.course_groups.models import CourseUserGroup
from xmodule.modulestore.django import modulestore
from collections import deque
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Создаёт когорты и ограничивает доступ к материалам курса."

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

        # 1. Включаем кохортизацию
        try:
            set_course_cohorted(course_key, cohorted=True)
            logger.info(f"Кохортизация включена для курса {course_id_str}")
        except Exception as e:
            logger.error(f"Не удалось включить кохортизацию для курса {course_id_str}: {str(e)}")
            return

        # 2. Создаём когорты
        self._create_cohorts(course_key, target_cohort_name, forbidden_cohort_name)

        # 3. Получаем структуру курса
        store = modulestore()
        with store.bulk_operations(course_key):
            course = store.get_course(course_key, depth=3)
            if not course:
                logger.warning(f"Курс {course_id_str} не найден в Studio. Когорты созданы, но материалы не настроены.")
                return

            # 4. Ищем первые 3 подраздела
            first_three_subs = self._get_first_n_subsections(course, n=3)

            # 5. Обрабатываем оставшиеся подразделы
            for section in course.get_children():
                for subsection in section.get_children():
                    if subsection not in first_three_subs:
                        self._restrict_block_visibility(subsection, [target_cohort_name, forbidden_cohort_name], course_key)

        logger.info("Настройка завершена.")

    def _create_cohorts(self, course_key, target_cohort_name, forbidden_cohort_name):
        """Создаёт когорты, если они не существуют."""
        for name in [target_cohort_name, forbidden_cohort_name]:
            if not is_cohort_exists(course_key, name):
                try:
                    add_cohort(course_key, name, assignment_type="manual")
                    logger.info(f"Когорта '{name}' создана для курса {course_key}")
                except Exception as e:
                    logger.error(f"Ошибка создания когорты '{name}': {str(e)}")

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

    def _restrict_block_visibility(self, block, allowed_cohort_names, course_key):
        """Ограничивает доступ к блоку для участников указанных когорт."""
        from openedx.core.djangoapps.course_groups.models import CourseUserGroup

        try:
            allowed_cohorts = CourseUserGroup.objects.filter(
                course_id=course_key,
                group_type=CourseUserGroup.COHORT,
                name__in=allowed_cohort_names
            )
            group_ids = [cohort.id for cohort in allowed_cohorts]
            
            # Устанавливаем ограничения доступа
            block.group_access = {
                "enabled": True,
                "cohorts": group_ids
            }
            modulestore().update_item(block, ModuleStoreEnum.UserID.test)
            logger.info(f"Доступ к блоку {block.location} ограничен для когорт {allowed_cohort_names}")
        except Exception as e:
            logger.error(f"Ошибка настройки доступа для блока {block.location}: {str(e)}")
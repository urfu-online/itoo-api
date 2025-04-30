# your_app/signals.py
from django.dispatch import receiver
from student.models import CourseEnrollment
from openedx.core.djangoapps.course_groups.cohorts import (
    add_user_to_cohort,
    is_cohort_exists,
    add_cohort,
    set_course_cohorted,
    get_cohort,
)
from openedx.core.djangoapps.course_groups.models import CourseUserGroup
from social_django.models import UserSocialAuth
from django.db.models.signals import post_save
from django.core.cache import cache
import logging
from itoo_api.models import CohortRule

logger = logging.getLogger(__name__)

CACHE_KEY_PREFIX = "cohort_rule_"
CACHE_TTL = 300  # 5 минут

def get_cached_rules(course_id):
    """Получение кэшированных правил для курса."""
    cache_key = f"{CACHE_KEY_PREFIX}{course_id}"
    cached = cache.get(cache_key)
    if cached:
        return [CohortRule(**rule) for rule in cached]
    return None

def set_cached_rules(course_id, rules):
    """Сохранение правил в кэше."""
    cache_key = f"{CACHE_KEY_PREFIX}{course_id}"
    serialized = [rule.to_dict() for rule in rules]
    cache.set(cache_key, serialized, timeout=CACHE_TTL)

class CohortRule:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def to_dict(self):
        return self.__dict__

@receiver(post_save, sender=CohortRule)
def clear_cache_on_rule_update(sender, instance, **kwargs):
    """Очистка кэша при обновлении правила."""
    cache_key = f"{CACHE_KEY_PREFIX}{instance.course_id}"
    cache.delete(cache_key)

@receiver(post_save, sender='student.CourseEnrollment')
def handle_course_enrollment(sender, instance, created, **kwargs):
    if not created or not instance.is_active:
        return

    course_key = instance.course_id
    user = instance.user

    try:
        # Получаем правила из кэша или БД
        rules = get_cached_rules(str(course_key))
        if not rules:
            rules = list(CohortRule.objects.filter(
                course_id=str(course_key), is_active=True
            ))
            set_cached_rules(str(course_key), rules)

        if not rules:
            return

        # Перебираем все правила
        applied = False
        for rule in rules:
            email_match = user.email.endswith(rule.email_domain)
            linked_with_provider = UserSocialAuth.objects.filter(
                user=user, provider=rule.provider
            ).exists()

            if email_match or linked_with_provider:
                _move_to_cohort(user, course_key, rule)
                applied = True

        if not applied:
            logger.info(f"User {user.username} did not match any cohort rules.")

    except Exception as e:
        logger.error(f"Error processing enrollment for {user.username}: {str(e)}", exc_info=True)

def _move_to_cohort(user, course_key, rule):
    target_cohort_name = rule.target_cohort_name
    
    try:
        # Включаем кохортизацию (если ещё не включена)
        set_course_cohorted(course_key, cohorted=True)

        # Создаём когорту, если её нет
        if not is_cohort_exists(course_key, target_cohort_name):
            add_cohort(course_key, target_cohort_name, assignment_type="manual")
            logger.info(f"Created cohort '{target_cohort_name}' for course {course_key}")

        target_cohort = CourseUserGroup.objects.get(
            course_id=course_key,
            group_type=CourseUserGroup.COHORT,
            name=target_cohort_name
        )

        # Проверяем текущую когорту пользователя
        current_cohort = get_cohort(user, course_key)
        
        # Исключаем пользователей из запрещённых когорт
        forbidden_cohorts = rule.get_forbidden_cohorts()
        if current_cohort and current_cohort.name in forbidden_cohorts:
            logger.info(f"Skipping {user.username}: restricted cohort '{current_cohort.name}'.")
            return

        # Если пользователь уже в целевой когорте - ничего не делаем
        if current_cohort and current_cohort.name == target_cohort_name:
            logger.info(f"{user.username} already in target cohort.")
            return

        # Удаляем из текущей когорты
        if current_cohort:
            current_cohort.users.remove(user)
            logger.info(f"Removed {user.username} from cohort '{current_cohort.name}'")

        # Добавляем в целевую
        target_cohort.users.add(user)
        logger.info(f"Moved {user.username} to cohort '{target_cohort_name}'")

    except Exception as e:
        logger.error(f"Error moving {user.username} to cohort: {str(e)}", exc_info=True)
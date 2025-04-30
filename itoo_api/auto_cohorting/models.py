# -*- coding: utf-8 -*-
from django.db import models
import json
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class CohortRule(models.Model):
    course_id = models.CharField(
        max_length=255,
        verbose_name="ID курса",
        help_text="Пример: course-v1:YourOrg+Course1+Run1"
    )
    target_cohort_name = models.CharField(
        max_length=255,
        default="Студенты УрФУ",
        verbose_name="Целевая когорта"
    )
    email_domain = models.CharField(
        max_length=255,
        default="@urfu.me",
        verbose_name="Домен email"
    )
    provider = models.CharField(
        max_length=255,
        default="keycloak",
        verbose_name="Провайдер аутентификации"
    )
    forbidden_cohorts = models.TextField(
        default='["Студенты УрФУ долг"]',
        verbose_name="Запрещённые когорты",
        help_text="JSON-массив названий когорт, куда нельзя перемещать пользователей."
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно"
    )

    def __str__(self):
        return "{} → {}".format(self.course_id, self.target_cohort_name)

    class Meta:
        verbose_name = "Правило когорты"
        verbose_name_plural = "Правила когорт"

    def get_forbidden_cohorts(self):
        """Возвращает список запрещённых когорт."""
        try:
            return json.loads(self.forbidden_cohorts)
        except json.JSONDecodeError:
            return []
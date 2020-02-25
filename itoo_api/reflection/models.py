# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel
import uuid

from django.contrib.auth.models import User
from itoo_api.models import Program


@python_2_unicode_compatible
class Reflection(TimeStampedModel):
    title = models.CharField("Наименование", max_length=255, null=True, blank=False)
    description = models.TextField("Описание", null=True, blank=True)
    program = models.ForeignKey(Program, null=True, blank=True, on_delete=models.CASCADE)

    # questions = models.ManyToManyField(Question, verbose_name='Вопросы', on_delete=models.PROTECT)
    # answers = models.ManyToManyField(Answer, verbose_name='Ответы', on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Рефлексия"
        verbose_name_plural = "Рефлексии"

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Question(TimeStampedModel):
    title = models.CharField("Текст вопроса", max_length=256, blank=False, null=True)
    order = models.PositiveSmallIntegerField("Порядок отрисовки", blank=True, null=True)
    reflection = models.ForeignKey(Reflection, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return str(self.pk)


@python_2_unicode_compatible
class Answer(TimeStampedModel):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    answer_text = models.TextField("Ответ в формате текст", blank=True, null=True)
    answer_float = models.FloatField("Ответ в формате числа", blank=True, null=True)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return str(self.user.email)

# @python_2_unicode_compatible
# class ResultAnswer(TimeStampedModel):
#     user = models.OneToOneField(User, unique=True, db_index=True, related_name='reflection',
#                                 verbose_name="Пользователь", on_delete=models.CASCADE, null=True)
#     reflection = models.ForeignKey(Reflection, null=True, blank=True, on_delete=models.CASCADE)
#
#     class Meta:
#         verbose_name = "Вопрос"
#         verbose_name_plural = "Вопросы"
#
#     def __str__(self):
#         return str(self.user.email)

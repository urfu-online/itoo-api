# -*- coding: utf-8 -*-
"""
Database ORM models for payments prerequisites
"""

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from ..utils import generate_new_filename


@python_2_unicode_compatible
class Offer(models.Model):
    content = models.TextField(verbose_name="Текст оферты")

    def __str__(self):
        return self.content


@python_2_unicode_compatible
class Profile(models.Model):
    SEX = (('m', 'мужской'), ('f', 'женский'))
    DOCUMENT_TYPES = (('u', 'Удостоверение'), ('s', 'Сертификат'), ('n', 'Неуспеваемость'))

    EDUCATION_LEVEL = (('M', 'Среднее профессиональное'), ('H', 'Высшее'))

    first_name = models.CharField("Имя", max_length=255, null=False, blank=False)
    last_name = models.CharField("Фамилия", max_length=255, null=False, blank=False)
    second_name = models.CharField("Отчество", max_length=255, null=True, blank=True)
    sex = models.CharField("Пол", max_length=1, choices=SEX, null=False, blank=False)
    city = models.CharField("Город", max_length=256, null=True, blank=False)

    birth_date = models.CharField("Дата рождения", max_length=16, null=False, blank=False)
    phone = models.CharField("Телефон", max_length=255, null=False, blank=False)
    job = models.CharField("Место работы", max_length=2048, null=True, blank=True)
    position = models.CharField("Должность", max_length=2048, null=True, blank=True)
    address_register = models.TextField("Адрес регистрации", blank=True, null=True)

    claim_scan = models.FileField("Скан заявления", upload_to=generate_new_filename)

    series = models.CharField("Серия", max_length=8, null=True, blank=True)
    number = models.CharField("Номер", max_length=8, null=True, blank=True)
    issued_by = models.TextField("Кем выдан", null=True, blank=True)
    unit_code = models.CharField("Код подразделения", max_length=16, null=True, blank=True)
    issue_date = models.CharField("Дата выдачи", max_length=16, null=True, blank=True)

    passport_scan = models.FileField("Скан паспорта", upload_to=generate_new_filename)

    education_level = models.CharField("Уровень базового образования", max_length=1, choices=EDUCATION_LEVEL,
                                       null=False, blank=False)
    diploma_scan = models.FileField("Скан диплома", upload_to=generate_new_filename, null=True, blank=True)

    all_valid = models.BooleanField("Данные в доках слушателя совпадают и корректны", default=False)

    doc_forwarding = models.FileField("Скан заявления о пересылке", upload_to=generate_new_filename, null=True,
                                      blank=True)

    mail_index = models.CharField("Почтовый индекс", max_length=255, null=True, blank=True)
    country = models.CharField("Страна", default='Россия', max_length=255, null=True, blank=True)
    address_living = models.TextField("Адрес проживания", max_length=255, blank=True, null=True)

    user = models.OneToOneField(User, unique=True, db_index=True, related_name='verified_profile', verbose_name="Пользователь", on_delete=models.CASCADE, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    @classmethod
    def get_profile(cls, username):
        if cls.objects.select_related().filter(user__username=username).exists():
            return cls.objects.select_related().filter(user__username=username)
        else:
            return None

    def fio(self):
        if self.second_name:
            return "{last_name} {first_name} {second_name}".format(
                last_name=self.last_name,
                first_name=self.first_name,
                second_name=self.second_name
            )
        else:
            return "{last_name} {first_name}".format(
                last_name=self.last_name,
                first_name=self.first_name
            )

    def __str__(self):
        return self.fio()

    class Meta:
        verbose_name = 'анкета для зачисления'
        verbose_name_plural = 'анкеты для зачисления'

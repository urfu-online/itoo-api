# -*- coding: utf-8 -*-
"""
Database ORM models for payments prerequisites
"""

from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from ..utils import generate_new_filename
from ..models import Program
import logging
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

logging.basicConfig()
logger = logging.getLogger(__name__)


# @python_2_unicode_compatible
# class Offer(models.Model):
#     content = models.TextField(verbose_name="Текст оферты")
#
#     def __str__(self):
#         return self.content

@python_2_unicode_compatible
class ProfileOrganization(models.Model):
    title = models.CharField("Название организации", max_length=255, null=False, blank=False)
    email = models.EmailField("Почта для связи", max_length=254, null=True, blank=True)
    phone = models.CharField("Телефон", max_length=255, null=True, blank=True)
    head = models.CharField("Голова", max_length=255, null=True, blank=True)
    program = models.CharField("program slug", max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'организация для анкеты'
        verbose_name_plural = 'организации для анкет'


@python_2_unicode_compatible
class Profile(models.Model):
    SEX = (('m', 'мужской'), ('f', 'женский'))
    DOCUMENT_TYPES = (('u', 'Удостоверение'), ('s', 'Сертификат'), ('n', 'Неуспеваемость'))

    EDUCATION_LEVEL = (('M', 'Среднее профессиональное'), ('H', 'Высшее'))

    last_name = models.CharField("Фамилия", max_length=255, null=False, blank=False)
    first_name = models.CharField("Имя", max_length=255, null=False, blank=False)
    second_name = models.CharField("Отчество", max_length=255, null=True, blank=True)
    sex = models.CharField("Пол", max_length=1, choices=SEX, null=False, blank=False)
    birth_date = models.CharField("Дата рождения", max_length=16, null=False, blank=False)
    phone = models.CharField("Телефон", max_length=255, null=False, blank=False)

    city = models.CharField("Город", max_length=256, null=True, blank=False)
    job = models.CharField("Место работы", max_length=2048, null=True, blank=False)
    position = models.CharField("Должность", max_length=2048, null=True, blank=False)

    address_register = models.TextField("Адрес регистрации", blank=True, null=True)

    claim_scan = models.FileField("Скан заявления на зачисление в программу ", upload_to=generate_new_filename,
                                  null=True, blank=True)

    series = models.CharField("Серия", max_length=8, null=True, blank=False)
    number = models.CharField("Номер", max_length=8, null=True, blank=False)
    issued_by = models.TextField("Кем выдан", null=True, blank=False)
    unit_code = models.CharField("Код подразделения", max_length=16, null=True, blank=False)
    issue_date = models.CharField("Дата выдачи", max_length=16, null=True, blank=False)

    # passport_scan = models.FileField("Скан паспорта", upload_to=generate_new_filename, null=True, blank=True)

    education_level = models.CharField("Уровень базового образования", max_length=1, choices=EDUCATION_LEVEL,
                                       null=False, blank=False)
    # diploma_scan = models.FileField("Скан диплома", upload_to=generate_new_filename, null=True, blank=True)
    series_diploma = models.CharField("Серия документа об образовании", max_length=255, null=True, blank=False)
    number_diploma = models.CharField("Номер документа об образовании", max_length=255, null=True, blank=False)
    edu_organization = models.CharField("Образовательное учреждение", max_length=355, null=True, blank=True)
    specialty = models.CharField("Специальность (направление подготовки)", max_length=355, null=True, blank=True)
    year_of_ending = models.CharField("Год окончания", max_length=16, null=True, blank=True)

    all_valid = models.BooleanField("Данные в доках слушателя совпадают и корректны", default=False)

    doc_forwarding = models.FileField("Скан заявление о пересылке удостоверения слушателя почтой России",
                                      upload_to=generate_new_filename, null=True,
                                      blank=True)

    leader_id = models.CharField("Leader ID", max_length=355, null=True, blank=True)
    SNILS = models.CharField("Номер СНИЛС", max_length=355, null=True, blank=True)
    add_email = models.EmailField("Почта для связи", max_length=254, null=True, blank=True)

    birth_place = models.CharField("Место рождения", max_length=355, null=True, blank=True)
    job_address = models.CharField("Адрес работы", max_length=355, null=True, blank=True)

    manager = models.CharField("Ответственный", max_length=355, null=True, blank=True)

    mail_index = models.CharField("Почтовый индекс", max_length=255, null=True, blank=True)
    country = models.CharField("Страна", default='Россия', max_length=255, null=True, blank=True)
    address_living = models.TextField("Адрес проживания", max_length=255, blank=True, null=True)

    terms = models.BooleanField("Я принимаю условия использования и соглашаюсь с политикой конфиденциальности",
                                null=False, blank=False)

    user = models.OneToOneField(User, unique=True, db_index=True, related_name='verified_profile',
                                verbose_name="Пользователь", on_delete=models.CASCADE, null=True)

    prefered_org = models.ForeignKey(ProfileOrganization, blank=True, null=True, on_delete=models.PROTECT)

    admin_number = models.CharField("Номер согласия", max_length=355, null=True, blank=True)
    admin_diagnostics = models.BooleanField("Диагностики пройдены", default=False)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    @classmethod
    def get_profile(cls, user):
        if cls.objects.select_related().filter(user=user).exists():
            return cls.objects.select_related().filter(user=user)
        else:
            return None

    # def fio(self):
    #     # return  self.second_name
    #     if self.second_name.encode('utf-8'):
    #         return "{last_name} {first_name} {second_name}".format(
    #             last_name=self.last_name.encode('utf-8'),
    #             first_name=self.first_name.encode('utf-8'),
    #             second_name=self.second_name.encode('utf-8')
    #         )
    #     else:
    #         return "{last_name} {first_name}".format(
    #             last_name=self.last_name.encode('utf-8'),
    #             first_name=self.first_name.encode('utf-8')
    #         )

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = 'анкета для зачисления'
        verbose_name_plural = 'анкеты для зачисления'

    def to_dict_uni(self):
        identity_card = {
            "identityCardType": "1",  # Паспорт
            "idncrdSeries": self.series,
            "idncrdNumber": self.number,
            "idncrdDate": self.issue_date,
            "authority": self.issued_by,
        }
        uni_dict = {
            "lastName": self.last_name,
            "firstName": self.first_name,
            "middleName": self.second_name,
            "citizenship": "0",  # По умолчанию
            "gender": "female" if self.sex == "f" else "male",
            "birthDate": self.birth_date,
            "post": self.position,
            "placeOfEmployment": self.job,
            'identityCard': identity_card
        }
        return uni_dict

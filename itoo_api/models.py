# -*- coding: utf-8 -*-
"""
Database ORM models managed by this Django app
Please do not integrate directly with these models!!!  This app currently
offers one programmatic API -- api.py for direct Python integration.
"""
from __future__ import unicode_literals
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel
from django.contrib.auth.models import User

from verified_profile.models import Offer, Profile


@python_2_unicode_compatible
class OrganizationCustom(TimeStampedModel):
    title = models.CharField('Название', blank=False, null=False, max_length=1024, default="")
    short_name = models.CharField('Аббревиатура', blank=False, null=False, max_length=64, default="", unique=True)
    slug = models.CharField('Человеко-понятный уникальный идентификатор', blank=False, null=False, max_length=64,
                            default="", unique=True)
    description = models.TextField('Описание', blank=True, null=True)
    logo = models.ImageField(
        upload_to='org_logos',
        help_text='Please add only .PNG files for logo images. This logo will be used on Organization logo.',
        null=True, blank=True, max_length=255
    )
    image_background = models.ImageField(
        upload_to='org_background',
        help_text='Please add only .PNG files for background images. This image will be used on Organization background image.',
        null=True, blank=True
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_courses(self):
        return self.organizationcourse_set.all()

    class Meta:
        """ Meta class for this Django model """
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'


@python_2_unicode_compatible
class EduProject(TimeStampedModel):
    title = models.CharField('Название', blank=False, null=False, max_length=1024, default="")
    short_name = models.CharField('Аббревиатура', blank=False, null=False, max_length=64, default="", unique=True)
    slug = models.CharField('Человеко-понятный уникальный идентификатор', blank=False, null=False, max_length=64,
                            default="", unique=True)
    owner = models.ForeignKey(OrganizationCustom, related_name="projects", blank=True, null=True,
                              on_delete=models.SET_NULL)
    description = models.TextField('Описание', blank=True, null=True)
    logo = models.ImageField(
        upload_to='project_logos',
        help_text='Please add only .PNG files for logo images. This logo will be used on Edu project logo.',
        null=True, blank=True, max_length=255
    )
    image_background = models.ImageField(
        upload_to='project_background',
        help_text='Please add only .PNG files for background images. This image will be used on Edu project background image.',
        null=True, blank=True
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Образовательный проект'
        verbose_name_plural = 'Образовательные проекты'

    def content(self):
        return TextBlock.objects.filter(object_id=self.id, content_type__model="EduProject")


# @python_2_unicode_compatible
class Program(TimeStampedModel):
    title = models.CharField('Наименование', blank=False, null=False, max_length=1024, default="")
    abbreviation = models.CharField('Abbreviation', blank=False, null=False, max_length=64, default="", unique=True)
    slug = models.CharField('Человеко-понятный уникальный идентификатор', blank=False, null=False, max_length=64,
                            default="", unique=True)
    description = models.TextField('Описание', blank=True, null=True)
    logo = models.ImageField(
        upload_to='program_logos',
        help_text='Please add only .PNG files for logo images. This logo will be used on Program logo.',
        null=True, blank=True, max_length=255
    )
    image_background = models.ImageField(
        upload_to='program_background',
        help_text='Please add only .PNG files for background images. This image will be used on Program background image.',
        null=True, blank=True
    )
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(OrganizationCustom, related_name="programs", blank=True, null=True,
                              on_delete=models.SET_NULL)
    project = models.ForeignKey(EduProject, related_name="realized_programs", blank=True, null=True,
                                on_delete=models.SET_NULL)

    def get_courses(self):
        return self.programcourse_set.all()

    def content(self):
        return TextBlock.objects.filter(object_id=self.id, content_type__model="Program")

    @classmethod
    def get_program(cls, slug):
        if cls.objects.select_related().filter(slug=slug).exists():
            return cls.objects.select_related().filter(slug=slug).first()
        else:
            return None

    class Meta:
        verbose_name = "Program"
        verbose_name_plural = "Programs"

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class ProgramCourse(TimeStampedModel):
    course_id = models.CharField(max_length=255, db_index=True, verbose_name='ID Курса')
    program = models.ForeignKey(Program, db_index=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.course_id

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = 'Ссылка на курс(Программа)'
        verbose_name_plural = 'Ссылки на курс(Программы)'


@python_2_unicode_compatible
class OrganizationCourse(TimeStampedModel):
    course_id = models.CharField(max_length=255, db_index=True, verbose_name='ID Курса')
    org = models.ForeignKey(OrganizationCustom, db_index=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.course_id

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = 'Ссылка на курс(Организация)'
        verbose_name_plural = 'Ссылки на курс(Организации)'


class PayUrfuData(TimeStampedModel):
    data = models.TextField('Данные')
    pub_date = models.DateTimeField('Дата запроса', auto_now_add=True)

    # def __str__(self):
    #     return self.pub_date

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = 'Данные от PAY URFU'
        verbose_name_plural = 'Данные от PAY URFU'


@python_2_unicode_compatible
class TextBlock(TimeStampedModel):
    type_slug = models.CharField("Тип отображения", default="html", max_length=200)
    content = models.TextField("Контент", blank=True, default="")
    limit = models.Q(app_label='itoo_api', model='eduproject') | models.Q(app_label='itoo_api', model='eduprogram')

    content_type = models.ForeignKey(
        ContentType,
        verbose_name='content page',
        limit_choices_to=limit,
        null=True,
        blank=True,
    )

    object_id = models.PositiveIntegerField(
        verbose_name='related object',
        null=True,
    )

    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return "TextBlock"


# @python_2_unicode_compatible
# class EduProject(TimeStampedModel):
#     title = models.CharField('Наименование', blank=False, null=False, max_length=1024, default="")
#     owner = models.ForeignKey(OrganizationCustom, related_name="projects", blank=True, null=True,
#                               on_delete=models.SET_NULL)
#
#     class Meta:
#         verbose_name = "образовательный проект"
#         verbose_name_plural = "образовательные проекты"
#
#     def __str__(self):
#         return self.title


@python_2_unicode_compatible
class EnrollProgram(TimeStampedModel):
    user = models.ForeignKey(User, db_index=True, verbose_name="Пользователь", on_delete=models.CASCADE, null=True)
    program = models.ForeignKey(Program, db_index=True)

    @classmethod
    def get_enroll_program(cls, user, program):
        if cls.objects.select_related().filter(user=user, program=program).exists():
            return cls.objects.select_related().filter(user=user, program=program).first()
        else:
            return None

    def __str__(self):
        return self.user.username

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = 'Запись на программу'
        verbose_name_plural = 'Запись на прграммы'

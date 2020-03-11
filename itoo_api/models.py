# -*- coding: utf-8 -*-
"""
Database ORM models managed by this Django app
Please do not integrate directly with these models!!!  This app currently
offers one programmatic API -- api.py for direct Python integration.
"""

from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel
import uuid


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

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'


@python_2_unicode_compatible
class Direction(TimeStampedModel):
    title = models.CharField('Наименование', blank=False, null=False, max_length=1024, default="")
    identifier = models.CharField('Идентификатор', blank=False, null=False, max_length=64, default="", unique=True)

    def __str__(self):
        return self.title

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = 'Направление подготовки'
        verbose_name_plural = 'Направления подготовки'


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

    class Meta(object):
        verbose_name = 'Образовательный проект'
        verbose_name_plural = 'Образовательные проекты'

    def content(self):
        return TextBlock.objects.filter(object_id=self.id, content_type__model="EduProject")


@python_2_unicode_compatible
class Program(TimeStampedModel):
    ENROLLMENT_STATUSES = (("0", "Недоступна"), ("1", "Доступна"), ("2", "По датам (в разработке)"))
    title = models.CharField('Наименование', blank=False, null=False, max_length=1024, default="")
    short_name = models.CharField('Аббревиатура', blank=False, null=False, max_length=64, default="", unique=True)
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
    direction = models.ForeignKey(Direction, blank=True, null=True, on_delete=models.SET_NULL)
    enrollment_allowed = models.CharField("Доступность записи", choices=ENROLLMENT_STATUSES, max_length=1, default="2")
    id_unit_program = models.CharField("Программа ID", blank=True, null=True, max_length=64)
    edu_start_date = models.DateField("Дата начала программы", null=True, blank=True)
    edu_end_date = models.DateField("Дата завершения программы", null=True, blank=True)
    number_of_hours = models.PositiveSmallIntegerField("Количество часов", null=True, blank=True)
    issued_document_name = models.CharField("Выдаваемый Документ", null=True, blank=True, max_length=128)

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
        verbose_name = "Образовательная программа"
        verbose_name_plural = "Образовательные программы"

    def __str__(self):
        return self.title

    def export_students(self):
        """TODO: implement method from admin"""
        return None


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

    content_object = generic.GenericForeignKey('content_type', 'object_id')

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

    def __unicode__(self):
        return self.user.username

    def __str__(self):
        return self.user.username

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = 'Запись на программу'
        verbose_name_plural = 'Запись на программы'

    @classmethod
    def get_or_create_enrollment(cls, user, program):

        assert isinstance(program, Program)

        if user is None:
            user.save()

        enrollment, __ = cls.objects.get_or_create(
            user=user,
            program=program,
        )

        # # If there was an unlinked CEA, it becomes linked now
        # CourseEnrollmentAllowed.objects.filter(
        #     email=user.email,
        #     course_id=course_key,
        #     user__isnull=True
        # ).update(user=user)

        return enrollment

# -*- coding: utf-8 -*-
"""
Database ORM models managed by this Django app
Please do not integrate directly with these models!!!  This app currently
offers one programmatic API -- api.py for direct Python integration.
"""
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel


@python_2_unicode_compatible
class Program(TimeStampedModel):
    name = models.CharField(u'Название', blank=False, null=False, max_length=1024, default="")
    short_name = models.CharField(u'Аббревиатура', blank=False, null=False, max_length=64, default="", unique=True)
    slug = models.CharField(u'Человеко-понятный уникальный идентификатор', blank=False, null=False, max_length=64, default="", unique=True)
    description = models.TextField(u'Описание')
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

    def __str__(self):
        return self.name

    def get_courses(self):
        return self.program_course_set.all()

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = u'Программа'
        verbose_name_plural = u'Программы'


@python_2_unicode_compatible
class ProgramCourse(TimeStampedModel):
    course_id = models.CharField(max_length=255, db_index=True, verbose_name=u'ID Курса')
    program = models.ForeignKey(Program, db_index=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.course_id

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = u'Ссылка на курс(Программа)'
        verbose_name_plural = u'Ссылки на курс(Программы)'


@python_2_unicode_compatible
class OrganizationCustom(TimeStampedModel):
    name = models.CharField(u'Название', blank=False, null=False, max_length=1024, default="")
    short_name = models.CharField(u'Аббревиатура', blank=False, null=False, max_length=64, default="", unique=True)
    slug = models.CharField(u'Человеко-понятный уникальный идентификатор', blank=False, null=False, max_length=64, default="", unique=True)
    description = models.TextField(u'Описание')
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
        return self.name

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = u'Организация'
        verbose_name_plural = u'Организации'


@python_2_unicode_compatible
class OrganizationCourse(TimeStampedModel):
    course_id = models.CharField(max_length=255, db_index=True, verbose_name=u'ID Курса')
    org = models.ForeignKey(OrganizationCustom, db_index=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.course_id

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = u'Ссылка на курс(Организация)'
        verbose_name_plural = u'Ссылки на курс(Организации)'

# -*- coding: utf-8 -*-
"""
Database ORM models managed by this Django app
Please do not integrate directly with these models!!!  This app currently
offers one programmatic API -- api.py for direct Python integration.
"""
from __future__ import unicode_literals

import re
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel


@python_2_unicode_compatible
class Program(TimeStampedModel):
    name = models.CharField(u'Название', blank=False, null=False, max_length=1024, default="")
    short_name = models.CharField(u'Короткое название', blank=False, null=False, max_length=64, default="")
    description = models.TextField(u'Описание')
    logo = models.ImageField(        
        upload_to='program_logos',
        help_text='Please add only .PNG files for logo images. This logo will be used on certificates.',
        null=True, blank=True, max_length=255
        )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class ProgramCourse(TimeStampedModel):
    course_id = models.CharField(max_length=255, db_index=True, verbose_name=u'ID Курса')
    program = models.ForeignKey(Program, db_index=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.course_id

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = u'Ссылка на курс'
        verbose_name_plural = u'Ссылки на курс'

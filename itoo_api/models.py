# -*- coding: utf-8 -*-
"""
Database ORM models managed by this Django app
Please do not integrate directly with these models!!!  This app currently
offers one programmatic API -- api.py for direct Python integration.
"""

import re
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel


@python_2_unicode_compatible
class Program(TimeStampedModel):
    name = models.CharField('Название', blank=False, null=False, max_length=1024, default="")
    short_name = models.CharField('Короткое название', blank=False, null=False, max_length=64, default="")
    description = models.TextField('Описание')
    logo = models.ImageField(        
        upload_to='program_logos',
        help_text=_('Please add only .PNG files for logo images. This logo will be used on certificates.'),
        null=True, blank=True, max_length=255
        )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ProgramCourse(TimeStampedModel):
    course_id = models.CharField(max_length=255, db_index=True, verbose_name='ID Курса')
    program = models.ForeignKey(Program, db_index=True)
    active = models.BooleanField(default=True)

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = _('Ссылка на курс')
        verbose_name_plural = _('Ссылки на курс')

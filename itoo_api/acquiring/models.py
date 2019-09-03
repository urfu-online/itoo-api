# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel
from django.core.serializers.json import DjangoJSONEncoder
import json

class JSONField(models.TextField):
    """
    JSONField es un campo TextField que serializa/deserializa objetos JSON.
    Django snippet #1478

    Ejemplo:
        class Page(models.Model):
            data = JSONField(blank=True, null=True)

        page = Page.objects.get(pk=5)
        page.data = {'title': 'test', 'type': 3}
        page.save()
    """
    def to_python(self, value):
        if value == "":
            return None

        try:
            if isinstance(value, str):
                return json.loads(value)
        except ValueError:
            pass
        return value

    def from_db_value(self, value, *args):
        return self.to_python(value)

    def get_db_prep_save(self, value, *args, **kwargs):
        if value == "":
            return None
        if isinstance(value, dict):
            value = json.dumps(value, cls=DjangoJSONEncoder)
        return value


@python_2_unicode_compatible
class PayUrfuData(TimeStampedModel):
    data = models.TextField('Данные')
    pub_date = models.DateTimeField('Дата запроса')

    def __unicode__(self):
        return unicode(self.pub_date)

    class Meta(object):
        """ Meta class for this Django model """
        verbose_name = 'Данные от PAY URFU'
        verbose_name_plural = 'Данные от PAY URFU'
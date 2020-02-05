from django.db import models
from ..models import Program
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel


@python_2_unicode_compatible
class Offer(TimeStampedModel):
    SERVICE_TYPES = ((0, "Обучение по программам ДПО"),)
    title = models.CharField("Наименование", max_length=255, null=False, blank=False)
    offer_text = models.TextField("Текст договора оферты", blank=False, null=True)
    income_item = models.CharField("Статья доходов", max_length=255, null=False, blank=False)
    unit = models.CharField("Подразделение", max_length=255, null=False, blank=False)
    unit_account = models.CharField("Лицевой счет подразделения", max_length=255, null=False, blank=False)
    program = models.ForeignKey("Program", on_delete=models.SET_NULL)
    edu_start_date = models.DateField("Дата начала обучения", null=True, Blank=True)
    edu_end_date = models.DateField("Дата завершения обучения", null=True, Blank=True)
    edu_service_type = models.CharField("Вид образовательной услуги", choices=SERVICE_TYPES, max_length=255, null=False,
                                        blank=False)

    class Meta:
        verbose_name = "Оферта"
        verbose_name_plural = "Оферты"

    def __str__(self):
        return self.title


class Payment(models.Model):
    pass

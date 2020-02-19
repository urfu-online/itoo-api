from django.contrib.auth import get_user_model
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel
import uuid

from ..models import Program


@python_2_unicode_compatible
class Offer(TimeStampedModel):
    SERVICE_TYPES = (
        ("0", "Обучение по программам ДПО"),
    )
    STATUSES = (
        ("0", "active"),
        ("1", "disabled"),
    )

    title = models.CharField("Наименование", max_length=255, null=True, blank=False)
    offer_text = models.TextField("Текст договора оферты", blank=False, null=True)
    id_urfu = models.CharField("ИД_Openedurfu", null=True, blank=True, max_length=128)
    income_item = models.CharField("Статья доходов", max_length=255, null=True, blank=False)
    unit = models.CharField("Подразделение", max_length=255, null=True, blank=False)
    unit_account = models.CharField("Лицевой счет подразделения", max_length=255, null=True, blank=False)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    edu_start_date = models.DateField("Дата начала договора", null=True, blank=True)
    edu_end_date = models.DateField("Дата завершения договора", null=True, blank=True)
    edu_service_type = models.CharField("Вид образовательной услуги", choices=SERVICE_TYPES, default="0",
                                        max_length=1, null=False, blank=False)
    status = models.CharField("Статус оферты", choices=STATUSES, default="0",
                              max_length=1, null=False, blank=False)
    training_form = models.CharField("Форма обучения", null=True, blank=False, max_length=128)
    edu_program_cost = models.PositiveIntegerField("Стоимость образовательной программы", null=True, blank=False)
    edu_program_cost_date = models.DateField("Дата установки стоимости", null=True, blank=False)
    created_at = models.DateTimeField("Дата создания договора", auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField("Дата обновления договора", auto_now=True, blank=True, null=True)

    def to_pay_urfu(self):
        return dict()

    class Meta:
        verbose_name = "Оферта"
        verbose_name_plural = "Оферты"

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Payment(TimeStampedModel):
    PAYMENT_STATUSES = (
        ("0", "Created"),
        ("1", "Waited"),
        ("2", "Success"),
        ("3", "Failed"),
    )
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    payment_number = models.CharField("Код платежа", max_length=32, blank=True, null=True)
    payment_date = models.DateTimeField("Дата платежа", auto_now_add=True)
    verify_date = models.DateTimeField("Дата подтверждения платежа", blank=True, null=True)
    user = models.ForeignKey(get_user_model(), null=False)
    offer = models.ForeignKey(Offer, verbose_name="Оферта", on_delete=models.SET_NULL, null=True)
    status = models.CharField("Статус платежа", choices=PAYMENT_STATUSES, max_length=1, default="0")

    class Meta:
        verbose_name = "Плетёж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return str(self.payment_id)



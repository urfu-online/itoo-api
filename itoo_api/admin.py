""" Django admin pages for organization models """
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from itoo_api.models import Program


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    pass
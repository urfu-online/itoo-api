# -*- coding: utf-8 -*-
from django.contrib import admin
from itoo_api.acquiring.models import PayUrfuData


@admin.register(PayUrfuData)
class PayUrfuDataAdmin(admin.ModelAdmin):
    date_hierarchy = 'pub_date'

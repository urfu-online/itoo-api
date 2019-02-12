""" Django admin pages for organization models """
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from itoo_api.models import Program, ProgramCourse


class ProgramCourseInline(admin.TabularInline):
    model = ProgramCourse


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'logo', 'active',)
    list_filter = ('active',)
    ordering = ('name', 'short_name',)
    readonly_fields = ('created',)
    search_fields = ('name', 'short_name',)
    inlines = [ProgramCourseInline]


@admin.register(ProgramCourse)
class ProgramCourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'program', 'active')
    ordering = ('course_id', 'program__name',)
    search_fields = ('course_id', 'program__name', 'program__short_name',)
""" Django admin pages for organization models """
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django_summernote.admin import SummernoteInlineModelAdmin
from django.contrib.contenttypes.admin import GenericTabularInline

from itoo_api.models import Program, ProgramCourse, OrganizationCustom, OrganizationCourse, PayUrfuData, Profile
from itoo_api.models import EduProgram, EduProject, TextBlock


class ProgramCourseInline(admin.TabularInline):
    model = ProgramCourse

class ProgramCourseGInline(GenericTabularInline):
    model = ProgramCourse


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'logo', 'active',)
    list_filter = ('active',)
    ordering = ('name', 'short_name',)
    readonly_fields = ('created',)
    search_fields = ('name', 'short_name', 'slug')
    inlines = [ProgramCourseInline]


@admin.register(ProgramCourse)
class ProgramCourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'program', 'active')
    ordering = ('course_id', 'program__name',)
    search_fields = ('course_id', 'program__name', 'program__short_name',)


class OrganizationCourseInline(admin.TabularInline):
    model = OrganizationCourse


@admin.register(OrganizationCustom)
class OrganizationCustomAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'logo', 'active',)
    list_filter = ('active',)
    ordering = ('name', 'short_name',)
    readonly_fields = ('created',)
    search_fields = ('name', 'short_name', 'slug')
    inlines = [OrganizationCourseInline]


@admin.register(OrganizationCourse)
class OrganizationCourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'org', 'active')
    ordering = ('course_id', 'org__name',)
    search_fields = ('course_id', 'org__name', 'org__short_name',)


@admin.register(PayUrfuData)
class PayUrfuDataAdmin(admin.ModelAdmin):
    list_display = ('pub_date',)
    date_hierarchy = 'pub_date'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'second_name', 'all_valid')
    search_fields = ('user', 'first_name', 'last_name', 'second_name', 'city')
    list_filter = ('all_valid', 'education_level', 'city')


class TextBlockInline(GenericTabularInline, SummernoteInlineModelAdmin):
    model = TextBlock
    extra = 1


class EduProgramInline(admin.TabularInline):
    model = EduProgram


@admin.register(EduProject)
class EduProjectAdmin(admin.ModelAdmin):
    inlines = [TextBlockInline]


@admin.register(EduProgram)
class EduProgramAdmin(admin.ModelAdmin):
    fields = ('title', 'project', 'owner')
    inlines = [TextBlockInline, ProgramCourseGInline]

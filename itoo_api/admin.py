""" Django admin pages for organization models """
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django_summernote.admin import SummernoteInlineModelAdmin
from django.contrib.contenttypes.admin import GenericTabularInline

from itoo_api.models import EduProject, ProgramCourse, OrganizationCustom, OrganizationCourse, PayUrfuData, Profile
from itoo_api.models import Program, TextBlock, EnrollProgram


class ProgramCourseInline(admin.TabularInline):
    model = ProgramCourse


class ProgramCourseGInline(GenericTabularInline):
    model = ProgramCourse


class TextBlockInline(GenericTabularInline, SummernoteInlineModelAdmin):
    model = TextBlock
    extra = 1


class ProgramInline(admin.TabularInline):
    model = Program


@admin.register(EnrollProgram)
class EnrollProgramAdmin(admin.ModelAdmin):
    model = EnrollProgram
    list_display = ('user', 'program',)
    list_filter = ('program__title',)
    ordering = ('user', 'program__title')
    readonly_fields = ('created',)
    search_fields = ('user__username', 'program__slug', 'program__title')


@admin.register(EduProject)
class EduProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_name', 'slug', 'logo', 'active', 'owner')
    list_filter = ('active', 'owner')
    ordering = ('title', 'short_name',)
    readonly_fields = ('created',)
    search_fields = ('title', 'short_name', 'slug')
    inlines = [ProgramInline, TextBlockInline]


@admin.register(ProgramCourse)
class ProgramCourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'program', 'active')
    ordering = ('course_id', 'program__title',)
    search_fields = ('course_id', 'program__title', 'program__short_name',)


# @admin.register(EduProject)
# class EduProjectAdmin(admin.ModelAdmin):
#     inlines = [TextBlockInline]


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_name', 'slug', 'logo', 'active', 'owner')
    list_filter = ('active', 'owner')
    ordering = ('title', 'short_name',)
    readonly_fields = ('created',)
    search_fields = ('title', 'short_name', 'slug')
    inlines = [ProgramCourseInline, TextBlockInline]


class OrganizationCourseInline(admin.TabularInline):
    model = OrganizationCourse


@admin.register(OrganizationCustom)
class OrganizationCustomAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_name', 'logo', 'active',)
    list_filter = ('active',)
    ordering = ('title', 'short_name',)
    readonly_fields = ('created',)
    search_fields = ('title', 'short_name', 'slug')
    inlines = [OrganizationCourseInline]


@admin.register(OrganizationCourse)
class OrganizationCourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'org', 'active')
    ordering = ('course_id', 'org__title',)
    search_fields = ('course_id', 'org__title', 'org__short_name',)


@admin.register(PayUrfuData)
class PayUrfuDataAdmin(admin.ModelAdmin):
    list_display = ('pub_date',)
    date_hierarchy = 'pub_date'


def export_csv(modeladmin, request, queryset):
    import csv
    from django.utils.encoding import smart_str
    from django.http import HttpResponse
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=profile.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"ID"),
        smart_str(u"Username"),
        smart_str(u"City"),
    ])
    for obj in queryset:
        writer.writerow([
            smart_str(obj.pk),
            smart_str(obj.user),
            smart_str(obj.city),
        ])
    return response


export_csv.short_description = u"Export CSV"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'second_name', 'all_valid')
    search_fields = ('user__username', 'first_name', 'last_name', 'second_name', 'city')
    list_filter = ('all_valid', 'education_level', 'city')
    actions = [export_csv]


@admin.register(TextBlock)
class TextBlockAdmin(admin.ModelAdmin):
    list_display = ["type_slug", "content"]

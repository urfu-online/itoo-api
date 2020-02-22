""" Django admin pages for organization models """

# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django_summernote.admin import SummernoteInlineModelAdmin

from itoo_api.acquiring.models import Offer, Payment
from itoo_api.models import EduProject, ProgramCourse, OrganizationCustom, OrganizationCourse, PayUrfuData
from itoo_api.models import Program, TextBlock, EnrollProgram, Direction
from itoo_api.reflection.models import Reflection, Question, Answer
from verified_profile.models import Profile, ProfileOrganization

from lms.djangoapps.grades.new.course_grade_factory import CourseGradeFactory
from opaque_keys.edx.keys import CourseKey


import logging
logging.basicConfig()
logger = logging.getLogger(__name__)


class QuestionInline(admin.TabularInline):
    model = Question


@admin.register(Reflection)
class ReflectionAdmin(admin.ModelAdmin):
    model = Reflection
    list_display = ('title', 'description', 'program',)
    list_filter = ('program',)
    search_fields = ('title', 'program',)
    inlines = [QuestionInline, ]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    model = Answer
    list_display = ('user', 'question',)
    search_fields = ('user__email', 'user__username')


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    model = Offer
    list_display = ("title", 'income_item', 'unit', 'unit_account',)
    list_filter = ('unit', 'income_item', 'unit_account', 'program')
    search_fields = ("title", 'income_item', 'unit', 'unit_account',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    model = Payment
    list_display = ("payment_id", "payment_number", 'payment_date', 'verify_date', 'user', "offer", "status")
    list_filter = ('status',)
    readonly_fields = ("payment_id", "payment_number", 'payment_date', 'verify_date', 'user', "offer", "status")


class ProgramCourseInline(admin.TabularInline):
    model = ProgramCourse


class ProgramCourseGInline(GenericTabularInline):
    model = ProgramCourse


class TextBlockInline(GenericTabularInline, SummernoteInlineModelAdmin):
    model = TextBlock
    extra = 1


class ProgramInline(admin.TabularInline):
    model = Program


def export_csv_program_entoll(modeladmin, request, queryset):
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
        smart_str(u"Program"),
    ])
    for obj in queryset:
        writer.writerow([
            smart_str(obj.pk),
            smart_str(obj.user),
            smart_str(obj.program),
        ])
    return response


export_csv_program_entoll.short_description = u"Export CSV"


@admin.register(EnrollProgram)
class EnrollProgramAdmin(admin.ModelAdmin):
    model = EnrollProgram
    list_display = ('user', 'program',)
    list_filter = ('program__title',)
    ordering = ('user', 'program__title')
    readonly_fields = ('created',)
    search_fields = ('user__username', 'program__slug', 'program__title', 'user__email')
    actions = [export_csv_program_entoll]


@admin.register(EduProject)
class EduProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_name', 'slug', 'logo', 'active', 'owner')
    list_filter = ('active', 'owner')
    ordering = ('title', 'short_name',)
    readonly_fields = ('created',)
    search_fields = ('title', 'short_name', 'slug')
    inlines = [ProgramInline, TextBlockInline]


def export_csv_program_course_entoll(modeladmin, request, queryset):
    import csv
    from django.utils.encoding import smart_str
    from django.http import HttpResponse
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=profile.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"course_id"),
        smart_str(u"program"),
    ])
    for obj in queryset:
        writer.writerow([
            smart_str(obj.course_id),
            smart_str(obj.program),
        ])
    return response


export_csv_program_entoll.short_description = u"Export CSV"


@admin.register(ProgramCourse)
class ProgramCourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'program', 'active')
    ordering = ('course_id', 'program__title',)
    search_fields = ('course_id', 'program__title', 'program__short_name',)
    actions = [export_csv_program_course_entoll]


# @admin.register(EduProject)
# class EduProjectAdmin(admin.ModelAdmin):
#     inlines = [TextBlockInline]
@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'identifier')
    list_filter = ('title',)
    ordering = ('title',)
    readonly_fields = ('created',)
    search_fields = ('title',)


# class ProfileOrganizationInline(admin.TabularInline):
#     model = ProfileOrganization

@admin.register(ProfileOrganization)
class ProfileOrganizationAdmin(admin.ModelAdmin):
    list_display = ("title", "program")


def export_csv_program(modeladmin, request, queryset):
    import csv
    from django.utils.encoding import smart_str
    from django.http import HttpResponse
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=profile.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    # writer.writerow([
    #     smart_str(u"course_id"),
    #     smart_str(u"program"),
    # ])

    example_program = queryset[0]
    logger.warning(example_program)

    enrollments = EnrollProgram.objects.filter(program=example_program)

    logger.warning(enrollments)

    head_row = ["email"]

    # writer.writerow("email")

    for course in example_program.get_courses():
        head_row.append(course.course_id)
    writer.writerow(head_row)

    for enroll in enrollments:
        row = [smart_str(enroll.user.email)]
        course_key = CourseKey.from_string(course.course_id)
        for course in example_program.get_courses():
            row.append(CourseGradeFactory().read(enroll.user, course_key).summary)
        logger.warning(row)
        writer.writerow(row)
    return response


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_name', 'slug', 'logo', 'active', 'owner')
    list_filter = ('active', 'owner')
    ordering = ('title', 'short_name',)
    readonly_fields = ('created',)
    search_fields = ('title', 'short_name', 'slug')
    inlines = [ProgramCourseInline, TextBlockInline]
    actions = [export_csv_program]



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


def export_csv_profile(modeladmin, request, queryset):
    import csv
    from django.utils.encoding import smart_str
    from django.http import HttpResponse
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=profile.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"ID"),
        smart_str(u"User ID"),
        smart_str(u"Username"),
        smart_str(u"email"),
        smart_str(u"last_name"),
        smart_str(u"first_name"),
        smart_str(u"second_name"),
        smart_str(u'sex'),
        smart_str(u'birth_date'),
        smart_str(u'phone'),
        smart_str(u'series'),
        smart_str(u'number'),
        smart_str(u'issued_by'),
        smart_str(u'unit_code'),
        smart_str(u'issue_date'),
        smart_str(u'address_register'),
        smart_str(u'country'),
        smart_str(u"City"),
        smart_str(u'address_living'),
        smart_str(u'mail_index'),
        smart_str(u"Job"),
        smart_str(u'position'),
        smart_str(u"edu_organization"),
        smart_str(u'education_level'),
        smart_str(u'specialty'),
        smart_str(u'series_diploma'),
        smart_str(u'number_diploma'),
        smart_str(u'year_of_ending'),
        smart_str(u'leader_id'),
        smart_str(u'SNILS'),
        smart_str(u'add_email'),
        smart_str(u'birth_place'),
        smart_str(u'job_address'),
    ])
    for obj in queryset:
        writer.writerow([
            smart_str(obj.pk),
            smart_str(obj.user.id),
            smart_str(obj.user),
            smart_str(obj.user.email),
            smart_str(obj.last_name),
            smart_str(obj.first_name),
            smart_str(obj.second_name),
            smart_str(obj.sex),
            smart_str(obj.birth_date),
            smart_str(obj.phone),
            smart_str(obj.series),
            smart_str(obj.number),
            smart_str(obj.issued_by),
            smart_str(obj.unit_code),
            smart_str(obj.issue_date),
            smart_str(obj.address_register),
            smart_str(obj.country),
            smart_str(obj.city),
            smart_str(obj.address_living),
            smart_str(obj.mail_index),
            smart_str(obj.job),
            smart_str(obj.position),
            smart_str(obj.edu_organization),
            smart_str(obj.education_level),
            smart_str(obj.specialty),
            smart_str(obj.series_diploma),
            smart_str(obj.number_diploma),
            smart_str(obj.year_of_ending),
            smart_str(obj.leader_id),
            smart_str(obj.SNILS),
            smart_str(obj.add_email),
            smart_str(obj.birth_place),
            smart_str(obj.job_address),
        ])
    return response


export_csv_profile.short_description = u"Export CSV"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'second_name', 'all_valid', 'manager')
    search_fields = ('user__username', 'first_name', 'last_name', 'second_name', 'city', 'user__email')
    list_filter = ('all_valid', 'education_level', 'manager', 'city',)
    actions = [export_csv_profile]


@admin.register(TextBlock)
class TextBlockAdmin(admin.ModelAdmin):
    list_display = ["type_slug", "content"]

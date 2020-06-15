# coding=utf-8
""" Django admin pages for organization models """
import logging

from celery import shared_task
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models
from django.forms import Textarea
from django_summernote.admin import SummernoteInlineModelAdmin
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment

from itoo_api.acquiring.models import Offer, Payment
from itoo_api.models import EduProject, ProgramCourse, OrganizationCustom, OrganizationCourse, PayUrfuData
from itoo_api.models import Program, TextBlock, EnrollProgram, Direction
from itoo_api.reflection.models import Reflection, Question, Answer
from verified_profile.models import Profile, ProfileOrganization

logging.basicConfig()
logger = logging.getLogger(__name__)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    model = Question


class QuestionInline(admin.StackedInline):
    model = Question
    show_change_link = True


@admin.register(Reflection)
class ReflectionAdmin(admin.ModelAdmin):
    model = Reflection
    list_display = ('title', 'description', 'program',)
    list_filter = ('program',)
    search_fields = ('title', 'program',)
    show_change_link = True
    inlines = [QuestionInline, ]


def export_csv_answer(modeladmin, request, queryset):
    import csv
    from django.utils.encoding import smart_str
    from django.http import HttpResponse
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=reflection.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"Username"),
        smart_str(u"Вопрос"),
        smart_str(u"Ответ"),
    ])
    for obj in queryset:
        writer.writerow([
            smart_str(obj.user),
            smart_str(obj.question),
            smart_str(obj.answer_text),
        ])
    return response


export_csv_answer.short_description = u"Export CSV"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    model = Answer
    list_display = ('user', 'question',)
    search_fields = ('user__email', 'user__username')
    actions = [export_csv_answer]


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


def update_programs_uuids(modeladmin, request, queryset):
    import csv, requests, json
    from django.utils.encoding import smart_str
    from django.http import HttpResponse
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=uni_programs.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"ID"),
        smart_str(u"Slug"),
        smart_str(u"Title"),
        smart_str(u"UUID"),
    ])
    programs_url = 'http://10.74.225.206:9085/programs'
    programs_response = requests.get(programs_url, json={}, auth=('openedu', 'openedu'))
    uni_programs = json.loads(programs_response.text)
    result = list()

    for uni_program in uni_programs:
        _progs = Program.objects.filter(title=uni_program["title"])
        for p in _progs:
            p.update(id_unit_program=uni_program["uuid"])
            result.append([p.pk, p.slug, p.title, p.uuid])

    for p in result:
        writer.writerow([
            smart_str(p.pk),
            smart_str(p.slug),
            smart_str(p.title),
            smart_str(p.uuid),
        ])
    return response


export_csv_program_entoll.short_description = u"Export CSV"
update_programs_uuids.short_description = u"Update uuids from UNI"
update_programs_uuids.acts_on_all = True

from django import forms


class EnrollProgramForm(forms.ModelForm):

    def save(self, *args, **kwargs):
        program_enrollment = super(EnrollProgramForm, self).save(commit=False)
        user = self.cleaned_data['user']
        program = self.cleaned_data['program']
        logger.warning(type(program))
        logger.warning(program)
        logger.warning('!!!!!!!!!!!!!')
        enrollment = EnrollProgram.get_or_create_enrollment(user, program)
        program_enrollment.id = enrollment.id
        program_enrollment.created = enrollment.created
        return program_enrollment

    class Meta:
        model = EnrollProgram
        fields = '__all__'


@admin.register(EnrollProgram)
class EnrollProgramAdmin(admin.ModelAdmin):
    model = EnrollProgram
    list_display = ('user', 'program', 'get_program_slug')
    list_filter = ('program__title',)
    raw_id_fields = ('user', 'program')
    ordering = ('user', 'program__title')
    readonly_fields = ('created',)
    search_fields = ('user__username', 'program__slug', 'program__title', 'user__email')
    form = EnrollProgramForm
    actions = [export_csv_program_entoll]

    def get_program_slug(self, obj):
        return obj.program.slug

    def get_search_results(self, request, queryset, search_term):
        qs, use_distinct = super(EnrollProgramAdmin, self).get_search_results(request, queryset, search_term)

        # annotate each enrollment with whether the username was an
        # exact match for the search term
        qs = qs.annotate(exact_username_match=models.Case(
            models.When(user__username=search_term, then=models.Value(True)),
            default=models.Value(False),
            output_field=models.BooleanField()))

        # present exact matches first
        qs = qs.order_by('-exact_username_match', 'user__username')

        return qs, use_distinct

    def queryset(self, request):
        return super(EnrollProgramAdmin, self).queryset(request).select_related('user')


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


@shared_task
def export_csv_program(modeladmin, request, queryset):
    import csv
    from django.utils.encoding import smart_str
    from django.http import HttpResponse
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=profile_grade.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)

    profile_fields = ["last_name", "first_name", "second_name", "sex", "birth_date", "phone", "series", "number",
                      "issued_by", "unit_code", "issue_date", "address_register", "country", "city", "address_living",
                      "mail_index", "job", "position", "edu_organization", "education_level", "specialty",
                      "series_diploma", "number_diploma", "year_of_ending", "leader_id", "SNILS", "add_email",
                      "birth_place", "job_address"]

    example_program = queryset[0]
    logger.warning(example_program)
    program_enrollments = []
    for e_u in EnrollProgram.objects.filter(program=example_program):
        # current_profile = Profile.objects.get(user=e_u.user)
        program_enrollments.append(e_u.user)

    head_row = ["email"]
    for course in example_program.get_courses():
        head_row.append(course.course_id)
        for p_f in profile_fields:
            head_row.append(p_f)
    writer.writerow(head_row)

    for enroll in program_enrollments:
        row = [smart_str(enroll.email)]
        for course in example_program.get_courses():
            course_key = CourseKey.from_string(course.course_id)
            course_enrollments = CourseEnrollment.objects.users_enrolled_in(course_key)
            for student, course_grade, error in CourseGradeFactory().iter([enroll], course_key=course_key):
                if student in course_enrollments:
                    row.append(course_grade.summary['percent'])
                else:
                    row.append("Not enrolled")

        try:
            current_profile = Profile.objects.get(user=enroll)
        except Profile.DoesNotExist:
            current_profile = None

        for p_f in profile_fields:
            if current_profile is not None:
                row.append(smart_str(current_profile.__dict__[p_f]))
            else:
                row.append("-")

        writer.writerow(row)

    #
    # # writer.writerow("email")
    #

    #
    # for enroll in enrollments:
    #     row = [smart_str(enroll.user.email)]
    #     # course_key = CourseKey.from_string(course.course_id)
    #     for course in example_program.get_courses():
    #
    #         logger.warning(course)
    #         logger.warning(CourseGradeFactory().read(enroll.user, course=get_course_by_id(CourseKey.from_string(str(course)))))
    #         # row.append(.summary)
    #     logger.warning(row)
    #     writer.writerow(row)
    return response


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_name', 'slug', 'logo', 'active', 'owner', 'enrollment_allowed')
    list_filter = ('active', 'owner', 'enrollment_allowed')
    ordering = ('title', 'short_name',)
    readonly_fields = ('created',)
    search_fields = ('title', 'short_name', 'slug')
    inlines = [ProgramCourseInline, TextBlockInline]
    actions = [export_csv_program, update_programs_uuids]


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
        smart_str(u'Ответственный'),
        smart_str(u'Номер согласия'),
        smart_str(u'Диагностики пройдены')
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
            smart_str(obj.manager),
            smart_str(obj.admin_number),
            smart_str(obj.admin_diagnostics)
        ])
    return response


export_csv_profile.short_description = u"Export CSV"


class ProfileByProgramFilter(admin.SimpleListFilter):
    title = 'Profile by program'
    parameter_name = 'profile_by_program'

    def lookups(self, request, model_admin):
        filters_program = []
        for program in Program.objects.all():
            filters_program.append((program.id, program.slug))
        return filters_program

    def queryset(self, request, queryset):
        enrollments_list = []
        if not self.value():
            return queryset
        for enrollment in EnrollProgram.objects.filter(program__id=self.value()):
            enrollments_list.append(enrollment.user)
        return queryset.filter(user__in=enrollments_list)


class ProfileByProjectFilter(admin.SimpleListFilter):
    title = 'Profile by project'
    parameter_name = 'profile_by_project'

    def lookups(self, request, model_admin):
        filters_project = []
        for project in EduProject.objects.all():
            filters_project.append((project.id, project.title))
        return filters_project

    def queryset(self, request, queryset):
        enrollments_list = []
        if not self.value():
            return queryset
        for program in Program.objects.filter(project__id=self.value()):
            for enrollment in EnrollProgram.objects.filter(program=program):
                enrollments_list.append(enrollment.user)
        return queryset.filter(user__in=enrollments_list)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                ("manager", 'user',),
                ('terms', 'doc_forwarding'),
                ("prefered_org",),
                # ('created_at', 'updated_at'), ? unknown fields
                ("admin_number", "admin_diagnostics", "all_valid")
            )
        }),
        (None, {
            'fields': (
                ('last_name', 'first_name', 'second_name'),
                ("SNILS", "leader_id", "sex"),
                ('birth_date', 'birth_place', 'phone'),
                ('city', 'job', 'position'),
                ('job_address',),
                ('add_email',)
            )
        }),
        ("Адрес", {
            'fields': (
                ("country", "mail_index"),
                ("address_living",),
                ("unit_code", "issue_date")
            )
        }),
        ("Паспортные данные", {
            'fields': (
                ("series", "number"),
                ("issued_by",),
                ("unit_code", "issue_date")
            )
        }),
        ("Образование", {
            'fields': (
                ("education_level",),
                ("series_diploma", 'number_diploma'),
                ("edu_organization",),
                ("specialty", "year_of_ending")
            )
        })
    )
    list_display = ('user', 'first_name', 'last_name', 'second_name', 'phone', 'leader_id', 'all_valid',
                    'admin_diagnostics', 'manager', 'admin_number')
    search_fields = ('user__username', 'first_name', 'last_name', 'second_name', 'city', 'user__email')
    list_filter = ('all_valid', 'admin_diagnostics', ProfileByProgramFilter, ProfileByProjectFilter, 'manager')
    actions = [export_csv_profile]
    readonly_fields = ["terms"]
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2})},
    }


@admin.register(TextBlock)
class TextBlockAdmin(admin.ModelAdmin):
    list_display = ["type_slug", "content"]

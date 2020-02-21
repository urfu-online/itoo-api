# -*- coding: utf-8 -*-
import logging
# import json
import urllib

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from itoo_api.models import EnrollProgram, Program
from .forms import ProfileForm, ProfileFormIPMG
from .models import Profile, ProfileOrganization

from student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView

logging.basicConfig()
logger = logging.getLogger(__name__)


# TODO : CLASSED BASSED TURBO VIEW ::::
# class ProfileDetail(DetailView):
#     model = Profile
#     has_program = None
#     program = None
#     slug = None
#     profile_state = None
#     profile = None
#
#     def get_context_data(self, **kwargs):
#         context = super(ProfileDetail, self).get_context_data(**kwargs)
#         context['has_program'] = self.has_program
#         context['profile_state'] = self.profile_state
#         context['program'] = self.program
#         context['profile'] = self.profile
#         return context
#
#     def get_success_url(self, **kwargs):
#         return reverse('itoo_api:verified_profile:profile_new', kwargs={'pk': kwargs['id']})
#
#     def get(self, request, *args, **kwargs):
#         user = request.user
#
#         try:
#             self.profile = Profile.get_profile(user=user)
#         except:
#             return redirect(self.get_success_url(id=user.id))
#
#         self.slug = request.GET.get('program_slug', None)
#         self.program = Program.get_program(slug=self.slug)
#         if self.program:
#             enroll = EnrollProgram.get_enroll_program(user=user, program=self.program)
#         else:
#             self.has_enroll_program = False
#             self.object = self.get_object()
#             context = self.get_context_data(object=self.object)
#             return self.render_to_response(context)
#             # return render(request, '../templates/profile_detail.html',
#             #               {'profile': profile, 'has_enroll_program': has_enroll_program, "program": None})
#         if enroll:
#             self.has_enroll_program = True
#             self.object = self.get_object()
#             context = self.get_context_data(object=self.object)
#             return self.render_to_response(context)
#             # return render(request, '../templates/profile_detail.html',
#             #               {'profile': profile, 'has_enroll_program': has_enroll_program, 'program': program})
#         else:
#             self.has_enroll_program = False
#             self.object = self.get_object()
#             context = self.get_context_data(object=self.object)
#             return self.render_to_response(context)
#             # return render(request, '../templates/profile_detail.html',
#             #               {'profile': profile, 'has_enroll_program': has_enroll_program, 'program': program})
#
#
# class ProfileCreate(CreateView):
#     model = Profile
#     has_program = None
#     program = None
#     slug = None
#     profile_state = None
#
#     def get_context_data(self, **kwargs):
#         context = super(ProfileCreate, self).get_context_data(**kwargs)
#         context['has_program'] = self.has_program
#         context['profile_state'] = self.profile_state
#         context['program'] = self.program
#         return context
#
#     def get(self, request, *args, **kwargs):
#         self.slug = request.session.get("slug", None)
#         if self.slug:
#             self.has_program = True
#             self.program = Program.get_program(slug=self.slug)
#         else:
#             self.has_program = False
#         self.profile_state = True
#         return self.render_to_response(self.get_context_data())
#
#     def post(self, request, *args, **kwargs):
#         self.request.session.set_test_cookie()
#         self.slug = self.request.session.get('slug', None)
#         if self.slug:
#             self.has_program = True
#             self.program = Program.get_program(slug=self.slug)
#         else:
#             self.has_program = False
#         form = self.get_form()
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)
#
#     def form_valid(self, form):
#         self.profile_state = True
#         profile = form.save(commit=False)
#         profile.user = self.request.user
#         profile.save()
#         EnrollProgram.objects.get_or_create(user=profile.user, program=self.program)
#
#         if EnrollProgram.get_enroll_program(user=profile.user, program=self.program):
#             course_keys = [CourseKey.from_string(course.course_id) for course in self.program.get_courses()]
#             for course_key in course_keys:
#                 if not CourseEnrollment.is_enrolled(user=profile.user, course_key=course_key):
#                     CourseEnrollment.enroll(user=profile.user, course_key=course_key, mode='audit',
#                                             check_access=True)
#         return redirect('https://courses.openedu.urfu.ru/npr/{}'.format(self.slug))
#
#     def form_invalid(self, form):
#         self.profile_state = False
#         context = {
#             'has_program': self.has_program,
#             'profile_state': self.profile_state,
#             "program": self.program,
#             'form': form
#         }
#         return render(self.request, '../templates/profile_new.html', context)
#
#
# class ProfileUpdate(UpdateView):
#     model = Profile


def redirect_params(url, params=None):
    response = redirect(url)
    if params:
        logger.warning(params)
        query_string = urllib.urlencode(params)
        logger.warning(query_string)
        response['Location'] += '?' + query_string
    return response


def profile_new(request):
    if request.method == "POST":
        logger.warning(request)
        request.session.set_test_cookie()
        form = ProfileForm(request.POST, request.FILES)
        slug = request.session.get('slug', None)
        if slug in ["IPMG", "IPMG_test"]:
            form = ProfileFormIPMG(request.POST, request.FILES)

        program = None
        if slug:
            has_program = True
            program = Program.get_program(slug=slug)
        else:
            has_program = False


        if form.is_valid() and program:
            profile_state = True
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            EnrollProgram.objects.get_or_create(user=profile.user, program=program)

            if EnrollProgram.get_enroll_program(user=profile.user, program=program):
                course_keys = [CourseKey.from_string(course.course_id) for course in program.get_courses()]
                for course_key in course_keys:
                    if not CourseEnrollment.is_enrolled(user=profile.user, course_key=course_key):
                        CourseEnrollment.enroll(user=profile.user, course_key=course_key, mode='audit',
                                                check_access=True)

                        # print(CourseEnrollment.is_enrolled(user=user, course_key=course_key), user, course_key)
                        # CourseEnrollment.enroll(user=user, course_key=course_key, mode='audit', check_access=True)
            if slug in ["IPMG", "IPMG_test"]:
                return redirect('https://courses.openedu.urfu.ru/npr/{}'.format(slug))
            else:
                return redirect('https://courses.openedu.urfu.ru/npr/{}'.format(slug))
        else:
            profile_state = False
            context = {
                'has_program': has_program,
                'profile_state': profile_state,
                "program": program,
                'form': form
            }
            if slug in ["IPMG", "IPMG_test"]:
                return render(request, '../templates/IPMG/profile_new.html', context)
            else:
                return render(request, '../templates/profile_new.html', context)

    elif request.method == "GET":
        user = request.user
        if not user.is_authenticated():
            slug = request.GET.get('program_slug', None)
            if slug:
                request.session["slug"] = slug
            return redirect('/login?next={}'.format(request.get_full_path()))
        program = None
        slug = request.session.get("slug", None)
        profile_organization = ProfileOrganization.objects.none()
        if slug:
            has_program = True
            program = Program.get_program(slug=slug)
            profile_organization = program.organizations
        else:
            has_program = False

        form = ProfileForm()
        if slug in ["IPMG", "IPMG_test"]:
            form = ProfileFormIPMG()

        profile_state = True
        template_scan = "Listener_state_({slug}).docx".format(slug=slug)
        context = {
            'form': form,
            "has_program": has_program,
            'profile_state': profile_state,
            "program": program,
            "template_scan": template_scan,
            "profile_organization": profile_organization
        }

        if slug in ["IPMG", "IPMG_test"]:
            return render(request, '../templates/IPMG/profile_new.html', context)
        else:
            return render(request, '../templates/profile_new.html', context)


def profile_edit(request):
    # launch = dict()
    user = request.user
    # profile = Profile.get_profile(user=user)[0]
    try:
        profile = Profile.get_profile(user=user)[0]
    except:
        return redirect(reverse('itoo:verified_profile:profile_new'))
    slug = request.session.get("slug", None)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if slug in ["IPMG", "IPMG_test"]:
            form = ProfileFormIPMG(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect("api/itoo_api/verified_profile/profile/?program_slug={}".format(slug))

        else:
            context = {
                'profile_state': False,
                'form': form
            }
            if slug in ["IPMG", "IPMG_test"]:
                return render(request, '../templates/IPMG/profile_edit.html', context)
            else:
                return render(request, '../templates/profile_edit.html', context)
            # return redirect(reverse('itoo:verified_profile:profile_detail'))

    elif request.method == "GET":
        form = ProfileForm(instance=profile)

        if slug in ["IPMG", "IPMG_test"]:
            form = ProfileFormIPMG(instance=profile)
        context = {
            'profile_state': True,
            'form': form
        }
        if slug in ["IPMG", "IPMG_test"]:
            return render(request, '../templates/IPMG/profile_edit.html', context)
        else:
            return render(request, '../templates/profile_edit.html', context)


def profile_edit_exist(request):
    # launch = dict()
    user = request.user

    profile = Profile.get_profile(user=user)[0]

    slug = request.GET.get('program_slug', None)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if slug in ["IPMG", "IPMG_test"]:
            form = ProfileFormIPMG(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            if slug in ["IPMG", "IPMG_test"]:
                return redirect('https://courses.openedu.urfu.ru/npr/{}'.format(slug))
            else:
                return redirect('https://courses.openedu.urfu.ru/npr/{}'.format(slug))

        else:
            context = {
                'profile_state': False,
                'form': form
            }
            if slug in ["IPMG", "IPMG_test"]:
                return render(request, '../templates/IPMG/profile_edit_exist.html', context)
            else:
                return render(request, '../templates/profile_edit_exist.html', context)
            # return redirect(reverse('itoo:verified_profile:profile_detail'))

    elif request.method == "GET":
        form = ProfileForm(instance=profile)
        if slug in ["IPMG", "IPMG_test"]:
            form = ProfileFormIPMG(instance=profile)

        context = {
            'profile_state': True,
            'form': form
        }
        if slug in ["IPMG", "IPMG_test"]:
            return render(request, '../templates/IPMG/profile_edit_exist.html', context)
        else:
            return render(request, '../templates/profile_edit_exist.html', context)


def profile_detail(request):
    user = request.user

    if not request.user.is_authenticated():
        slug = request.GET.get('program_slug', None)
        if slug:
            request.session["slug"] = slug
        return redirect('/login?next={}'.format(request.get_full_path()))

    if request.method == "GET":
        profile = Profile.get_profile(user=user)
        slug = request.GET.get('program_slug', None)
        if slug:
            request.session["slug"] = slug
        if not profile:
            # return redirect(reverse('itoo:verified_profile:profile_new', args=(slug, )))
            return redirect("api/itoo_api/verified_profile/profile/new/")
        else:
            program = Program.get_program(slug=slug)
            if program:
                enroll = EnrollProgram.get_enroll_program(user=user, program=program)
            else:
                has_enroll_program = False
                return render(request, '../templates/profile_detail.html',
                              {'profile': profile, 'has_enroll_program': has_enroll_program, "program": None})
            if enroll:
                has_enroll_program = True
                return render(request, '../templates/profile_detail.html',
                              {'profile': profile, 'has_enroll_program': has_enroll_program, 'program': program})
            else:
                has_enroll_program = False
                return render(request, '../templates/profile_detail.html',
                              {'profile': profile, 'has_enroll_program': has_enroll_program, 'program': program})

    elif request.method == "POST":
        slug = request.session.get("slug", None)
        program = Program.get_program(slug=slug)
        if slug and program:
            EnrollProgram.objects.get_or_create(user=user, program=program)

        if EnrollProgram.get_enroll_program(user=user, program=program):
            course_keys = [CourseKey.from_string(course.course_id) for course in program.get_courses()]
            for course_key in course_keys:
                if not CourseEnrollment.is_enrolled(user=user, course_key=course_key):
                    CourseEnrollment.enroll(user=user, course_key=course_key, mode='audit', check_access=True)

        # TODO: Что то придумать с этими с ифками
        else:
            slug = ''
        return redirect('https://courses.openedu.urfu.ru/npr/{}'.format(slug))

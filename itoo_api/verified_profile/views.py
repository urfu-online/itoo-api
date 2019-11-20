# -*- coding: utf-8 -*-
import logging
# import json
import urllib

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from itoo_api.models import EnrollProgram, Program
from .forms import ProfileForm
from .models import Profile

from student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView

logging.basicConfig()
logger = logging.getLogger(__name__)

# TODO : CLASSED BASSED TURBO VIEW ::::
# class ProfileDetail(DetailView):
#     model = Profile
#
#
# class ProfileCreate(CreateView):
#     model = Profile
#
#     def form_valid(self, form):
#         self.request.session.set_test_cookie()
#         form = ProfileForm(self.request.POST, self.request.FILES)
#         slug = self.request.session.get('slug', None)
#         program = None
#         if slug:
#             has_program = True
#             program = Program.get_program(slug=slug)
#         else:
#             has_program = False
#         profile_state = True
#         profile = form.save(commit=False)
#         profile.user = self.request.user
#         profile.save()
#         EnrollProgram.objects.get_or_create(user=profile.user, program=program)
#
#         if EnrollProgram.get_enroll_program(user=profile.user, program=program):
#             course_keys = [CourseKey.from_string(course.course_id) for course in program.get_courses()]
#             for course_key in course_keys:
#                 if not CourseEnrollment.is_enrolled(user=profile.user, course_key=course_key):
#                     CourseEnrollment.enroll(user=profile.user, course_key=course_key, mode='audit',
#                                             check_access=True)
#
#
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
            # profile_params = {
            #     'contract_number': 3,
            #     'client_name': "{first_name} {last_name} {second_name}".format(
            #         first_name=profile.first_name.encode('utf8'),
            #         last_name=profile.last_name.encode('utf8'),
            #         second_name=profile.second_name.encode('utf8')
            #     ),
            #     'client_phone': profile.phone,
            #     'client_email': request.user.email,
            #     'amount': '2000'
            # }
            return redirect('https://courses.openedu.urfu.ru/npr/{}'.format(slug))
        else:
            profile_state = False
            context = {
                'has_program': has_program,
                'profile_state': profile_state,
                "program": program,
                'form': form
            }
            return render(request, '../templates/profile_new.html', context)

    elif request.method == "GET":
        program = None
        slug = request.session.get("slug", None)
        if slug:
            has_program = True
            program = Program.get_program(slug=slug)
        else:
            has_program = False
        form = ProfileForm()
        profile_state = True
        context = {
            'form': form,
            "has_program": has_program,
            'profile_state': profile_state,
            "program": program
        }
        return render(request, '../templates/profile_new.html', context)


def profile_edit(request):
    # launch = dict()
    user = request.user
    profile = Profile.get_profile(user=user)[0]
    slug = request.session.get("slug", None)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect("api/itoo_api/verified_profile/profile/?program_slug={}".format(slug))
            # return redirect(reverse('itoo:verified_profile:profile_detail'))

    elif request.method == "GET":
        form = ProfileForm(instance=profile)
        return render(request, '../templates/profile_edit.html', {'form': form})


def profile_detail(request):
    user = request.user

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

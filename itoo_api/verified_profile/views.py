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
from django.contrib.auth.decorators import login_required

from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from itoo_api.verified_profile.permission import IsLoggedInUserOrAdmin, IsAdminUser
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from itoo_api.serializers import ProfileSerializer

logging.basicConfig()
logger = logging.getLogger(__name__)


class ProfileDetail(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'program_slug'

    def get_object(self):
        slug = self.kwargs['program_slug']


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsLoggedInUserOrAdmin]
        elif self.action == 'list' or self.action == 'destroy':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


def redirect_params(url, params=None):
    response = redirect(url)
    if params:
        logger.warning(params)
        query_string = urllib.urlencode(params)
        logger.warning(query_string)
        response['Location'] += '?' + query_string
    return response


# @login_required(redirect_field_name='api/itoo_api/verified_profile/profile/?program_slug=IPMG')
def profile_new(request, slug):
    if request.method == "POST":
        logger.warning(request)
        request.session.set_test_cookie()
        form = ProfileForm(request.POST, request.FILES)
        slug = request.session.get('slug', slug)
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

        if user.is_anonymous():
          return redirect('/login?next={}'.format(request.get_full_path()))
        # if not user.is_authenticated():
        #     # slug = request.GET.get('program_slug', None)
        #     if slug:
        #         request.session["slug"] = slug
        #     return redirect('/login?next={}'.format('/api/itoo_api/verified_profile/profile/{}'.format(slug)))
        program = None
        slug = request.session.get("slug", slug)
        profile_organization = ProfileOrganization.objects.none()

        if slug:
            has_program = True
            program = Program.get_program(slug=slug)
            profile_organization = ProfileOrganization.objects.filter(program=program.slug)
        else:
            has_program = False

        form = ProfileForm()
        if slug in ["IPMG", "IPMG_test"]:
            form = ProfileFormIPMG()

        if has_program and form:
            form.fields["prefered_org"].queryset = profile_organization

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


# @login_required(redirect_field_name='/')
def profile_edit(request, slug):
    # launch = dict()
    user = request.user
    # profile = Profile.get_profile(user=user)[0]
    if user.is_anonymous():
        return redirect('/login?next={}'.format(request.get_full_path()))

    try:
        profile = Profile.get_profile(user=user)[0]
    except:
        return redirect(reverse('itoo:verified_profile:profile_new'))
    slug = request.session.get("slug", slug)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if slug in ["IPMG", "IPMG_test"]:
            form = ProfileFormIPMG(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect("api/itoo_api/verified_profile/profile/{}".format(slug))

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


def profile_edit_exist(request, slug):
    # launch = dict()
    user = request.user

    if user.is_anonymous():
        return redirect('/login?next={}'.format(request.get_full_path()))

    profile = Profile.get_profile(user=user)[0]

    # slug = request.GET.get('program_slug', None)
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


# @login_required(redirect_field_name='/api/itoo_api/verified_profile/profile/?program_slug=IPMG')
def profile_detail(request, slug):
    user = request.user

    if user.is_anonymous():
        return redirect('/login?next={}'.format(request.get_full_path()))
        # slug = request.GET.get('program_slug', None)
    if slug:
        request.session["slug"] = slug
        # return redirect('/login?next={}'.format('/api/itoo_api/verified_profile/profile/{}'.format(slug)))

    if request.method == "GET":
        profile = Profile.get_profile(user=user)
        if slug:
            request.session["slug"] = slug
        if not profile:
            # return redirect(reverse('itoo:verified_profile:profile_new', args=(slug, )))
            return redirect("api/itoo_api/verified_profile/profile/new/{}".format(slug))
        else:
            program = Program.get_program(slug=slug)
            if program:
                enroll = EnrollProgram.get_enroll_program(user=user, program=program)
            else:
                has_enroll_program = False
                if slug in ["IPMG", "IPMG_test"]:
                    return redirect('/api/itoo_api/verified_profile/profile/edit_exist/{}'.format(slug))
                else:
                    return render(request, '../templates/profile_detail.html',
                                  {'profile': profile, 'has_enroll_program': has_enroll_program, "program": None})
            if enroll:
                has_enroll_program = True
                if slug in ["IPMG", "IPMG_test"]:
                    return redirect('/api/itoo_api/verified_profile/profile/edit_exist/{}'.format(slug))
                else:
                    # return redirect('/api/itoo_api/verified_profile/profile/edit/{}'.format(slug))
                    return render(request, '../templates/profile_detail.html',
                              {'profile': profile, 'has_enroll_program': has_enroll_program, 'program': program})
            else:
                has_enroll_program = False
                if slug in ["IPMG", "IPMG_test"]:
                    return redirect('/api/itoo_api/verified_profile/profile/edit_exist/{}'.format(slug))
                else:
                    return redirect('/api/itoo_api/verified_profile/profile/edit/{}'.format(slug))
                    # return render(request, '../templates/profile_detail.html',
                    #               {'profile': profile, 'has_enroll_program': has_enroll_program, 'program': program})

    elif request.method == "POST":
        slug = request.session.get("slug", slug)
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

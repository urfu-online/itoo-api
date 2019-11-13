# -*- coding: utf-8 -*-
import logging
# import json
import urllib

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from itoo_api.models import EnrollProgram, Program
from .forms import ProfileForm
from .models import Profile

logging.basicConfig()
logger = logging.getLogger(__name__)


def redirect_params(url, params=None):
    response = redirect(url)
    if params:
        logger.warning(params)
        query_string = urllib.urlencode(params)
        logger.warning(query_string)
        response['Location'] += '?' + query_string
    return response


def profile_new(request, **kwargs):
    if request.method == "POST":
        logger.warning(request)
        form = ProfileForm(request.POST, request.FILES)
        program = Program.get_program(slug=kwargs['slug'])
        if form.is_valid() and program:
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            EnrollProgram.objects.get_or_create(user=profile.user, program=program)
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
            return redirect('https://courses.openedu.urfu.ru/npr')
        else:
            context = {
                'form': form
            }
            return render(request, '../templates/profile_new.html', context)

    elif request.method == "GET":
        logger.warning(request.GET)
        form = ProfileForm()
        context = {
            'form': form
        }
        return render(request, '../templates/profile_new.html', context)


def profile_edit(request):
    # launch = dict()
    user = request.user
    profile = Profile.get_profile(user=user)[0]
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect(reverse('itoo:verified_profile:profile_detail'))
        # logger.warning(request.body)
        # course_modes = request.body.course_modes
        # for mod in course_modes:
        #     launch = {
        #         'username': mod.username,
        #         'course_id': mod.course_id,
        #         'amount': mod.course_modes_min_price
        #     }
        # if Profile.objects.filter(User.username=launch['username']).exists():
        #     redirect('profile/')

    elif request.method == "GET":
        form = ProfileForm(instance=profile)
        return render(request, '../templates/profile_edit.html', {'form': form})


def profile_detail(request):
    user = request.user

    if request.method == "GET":
        profile = Profile.get_profile(user=user)
        slug = request.GET.get('program_slug', None)
        if profile == None:
            return redirect(reverse('itoo:verified_profile:profile_new', kwargs=(slug, )))
        else:
            return render(request, '../templates/profile_detail.html', {'profile': profile})

    elif request.method == "POST":
        # profile = Profile.get_profile(user=user)[0]
        # profile_params = {
        #     'contract_number': 3,
        #     'client_name': "{first_name} {last_name} {second_name}".format(
        #         first_name=profile.first_name.encode('utf8'),
        #         last_name=profile.last_name.encode('utf8'),
        #         second_name=profile.second_name.encode('utf8'),
        #     ),
        #     'client_phone': profile.phone,
        #     'client_email': request.user.email,
        #     'amount': '2000'
        # }
        return redirect('https://courses.openedu.urfu.ru/npr')

# -*- coding: utf-8 -*-
import logging
# import json
import urllib
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .forms import ProfileForm
from .models import Profile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.template import Context, Template
from xblock.fragment import Fragment
import pkg_resources

from django.core.urlresolvers import reverse

logging.basicConfig()
logger = logging.getLogger(__name__)


def redirect_params(url, params=None):
    response = redirect(url)
    if params:
        query_string = urllib.urlencode(params)
        response['Location'] += '?' + query_string
    return response


def profile_new(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.save()
            profile_params = {
                'contract_number': 3,
                'client_name': "{first_name} {last_name} {second_name}".format(
                    first_name=urllib.quote(profile.first_name),
                    last_name=urllib.quote(profile.last_name),
                    second_name=urllib.quote(profile.second_name)
                ),
                'client_phone': profile.phone,
                'client_email': request.user.email,
                'amount': '2000'
            }
            return redirect_params('https://ubu.urfu.ru/pay/', profile_params)
        else:
            context = {
                'form': form
            }
            return render(request, '../templates/profile_new.html', context)

    elif request.method == "GET":
        form = ProfileForm()
        context = {
            'form': form
        }
        return render(request, '../templates/profile_new.html', context)


def profile_edit(request):
    launch = dict()
    if request.method == "POST":
        logger.warning(request.body)
        course_modes = request.body.course_modes
        for mod in course_modes:
            launch = {
                'username': mod.username,
                'course_id': mod.course_id,
                'amount': mod.course_modes_min_price
            }
        # if Profile.objects.filter(User.username=launch['username']).exists():
        #     redirect('profile/')

    elif request.method == "GET":
        form = ProfileForm()
        return render(request, '../templates/profile_edit.html', {'form': form})

def profile_detail(request):
    user = request.user
    profile = Profile.get_profile(user=user)
    logger.warning(profile)
    if profile==None:
        return redirect(reverse('itoo:verified_profile:profile_new'))
    else:
        return render(request, '../templates/profile_detail.html', {'profile': profile})
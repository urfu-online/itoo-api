# -*- coding: utf-8 -*-
import logging
# import json
import urllib
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .forms import ProfileForm
from django.shortcuts import render, redirect
from django.template import Context, Template
from xblock.fragment import Fragment
import pkg_resources

logging.basicConfig()
logger = logging.getLogger(__name__)


def redirect_params(url, params=None):
    response = redirect(url)
    if params:
        query_string = urllib.urlencode(params)
        response['Location'] += '?' + query_string
    return response


def profile_new(request):
    launch = {}
    course_modes = request.POST.post('course_modes')
    logger.warning(course_modes)
    if request.method == "POST":
        if 'course_modes' in request.POST:
            course_modes = request.POST.post('course_modes')
            for mod in course_modes:
                launch = {
                    'username': mod.username,
                    'course_id': mod.course_id,
                    'amount': mod.course_modes_min_price
                }
            logger.warning("11111111111")
            logger.warning(launch)
        else:
            form = ProfileForm(request.POST, request.FILES)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.save()
                profile_params = {
                    'contract_number': 3,
                    'client_name': "{first_name} {last_name} {second_name}".format(
                        first_name=profile.first_name,
                        last_name=profile.last_name,
                        second_name=profile.second_name
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
                return render(request, '../templates/profile_edit.html', context)

    elif request.method == "GET":
        form = ProfileForm()
        context = {
            'form': form
        }
        return render(request, '../templates/profile_edit.html', context)

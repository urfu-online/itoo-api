# -*- coding: utf-8 -*-
import logging
# import json
import urllib
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .forms import ProfileForm
from django.shortcuts import render ,redirect
from django.template import Context, Template
from xblock.fragment import Fragment
import pkg_resources

logging.basicConfig()
logger = logging.getLogger(__name__)


# class VerifiedProfileView(APIView):
#     permission_classes = (AllowAny, )
def redirect_params(url, params=None):
    response = redirect(url)
    if params:
        query_string = urllib.urlencode(params)
        response['Location'] += '?' + query_string
    return response


def profile_new(request):
    # if request.method == 'GET':
    template_path = '../templates/profile_edit.html'
    if request.method == "POST":
        form = ProfileForm(request.POST)
        logger.debug(form.errors)
        logger.debug(str(form))
        if form.is_valid():
            form.save()
            profile_params = {
                'profile': form
            }
            logger.debug(profile_params)
            return redirect_params('https://ubu.urfu.ru/pay/', profile_params)
        else:
            context = {
                'form': form
            }
            return render(request, template_path, context)

    elif request.method == "GET":
        form = ProfileForm()
        context = {
            'form': form
        }
        return render(request, template_path, context)

    # return render(request, 'templates/profile_edit.html', {'form': form})


# def load_resource(resource_path):  # pragma: NO COVER
#     """
#     Gets the content of a resource
#     """
#     resource_content = pkg_resources.resource_string(__name__, resource_path)
#     return unicode(resource_content)
#
#
# def render_template(template_path, context=None):  # pragma: NO COVER
#     """
#     Evaluate a template by resource path, applying the provided context.
#     """
#     if context is None:
#         context = {}
#
#     template_str = load_resource(template_path)
#     template = Template(template_str)
#     return template.render(Context(context))

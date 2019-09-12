# -*- coding: utf-8 -*-
import logging
# import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .forms import ProfileForm
from django.shortcuts import render
from django.template import Context, Template
from xblock.fragment import Fragment
import pkg_resources

logging.basicConfig()
logger = logging.getLogger(__name__)


# class VerifiedProfileView(APIView):
#     permission_classes = (AllowAny, )

def profile_new(request):
    # if request.method == 'GET':
    form = ProfileForm()
    context = {
        'form': form
    }
    template_path = '../templates/profile_edit.html'
    template_str = load_resource(template_path)
    return render(request,template_path,context)

    # return render(request, 'templates/profile_edit.html', {'form': form})


def load_resource(resource_path):  # pragma: NO COVER
    """
    Gets the content of a resource
    """
    resource_content = pkg_resources.resource_string(__name__, resource_path)
    return unicode(resource_content)


def render_template(template_path, context=None):  # pragma: NO COVER
    """
    Evaluate a template by resource path, applying the provided context.
    """
    if context is None:
        context = {}

    template_str = load_resource(template_path)
    template = Template(template_str)
    return template.render(Context(context))

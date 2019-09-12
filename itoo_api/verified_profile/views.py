# -*- coding: utf-8 -*-
import logging
# import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .forms import ProfileForm
from django.shortcuts import render


logging.basicConfig()
logger = logging.getLogger(__name__)


class VerifiedProfileView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request):
        form = ProfileForm()
        return render(request, 'itoo_api/verified_profile/templates/profile_edit.html', {'form': form})
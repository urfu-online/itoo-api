# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from itoo_api.verified_profile.views import *

# from rest_framework import routers
#
# router_list = routers.DefaultRouter()
# router_list.register(r'courses_mode_all', CourseModeListAllViewSet)

app_name = 'verified_profile'
urlpatterns = [
    url(r'profile/', profile_new, name='profile_new'),
    url(r'profile_read/', profile_read, name='profile_read')
    # url(r'paid_course_cus/', PaidCoursesCusViewSet, name='paid_course_cus')
    # url(r'^list/', include(router_list.urls)),
]
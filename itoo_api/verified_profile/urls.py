# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from itoo_api.verified_profile.views import *

# from rest_framework import routers
#
# router_list = routers.DefaultRouter()
# router_list.register(r'courses_mode_all', CourseModeListAllViewSet)

app_name = 'verified_profile'
urlpatterns = [
    url(r'profile/$', profile_detail, name='profile_redirect'),
    url(r'profile/(?P<slug>\w+)/$', profile_detail, name='profile_detail'),

    url(r'profile/new/(?P<slug>\w+)/$', profile_new, name='profile_new'),
    url(r'profile/edit/(?P<slug>\w+)/$', profile_edit, name='profile_edit'),
    url(r'profile/edit_exist/(?P<slug>\w+)/$', profile_edit_exist, name='profile_edit_exist')
    # url(r'paid_course_cus/', PaidCoursesCusViewSet, name='paid_course_cus')
    # url(r'^list/', include(router_list.urls)),
]

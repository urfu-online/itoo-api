from django.conf.urls import url, include
from itoo_api.acquiring.views import *

# from rest_framework import routers
#
# router_list = routers.SimpleRouter()
# router_list.register(r'paid_course_cus', PaidCoursesCusViewSet)

urlpatterns = [
    url(r'paid_courses_role/', PaidCoursesRoleViewSet.as_view(), name='paid_courses_role'),
    url(r'course_mode_change/',CourseModesChange.as_view(), name='course_mode_change'),
    url(r'paid_course_cus/', PaidCoursesCusViewSet, name='paid_course_cus')
    # url(r'^list/', include(router_list.urls)),
]
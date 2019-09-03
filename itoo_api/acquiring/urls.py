from django.conf.urls import url, include
from itoo_api.acquiring.views import *

from rest_framework import routers

router_list = routers.DefaultRouter()
router_list.register(r'courses_mode_all', CourseModeListAllViewSet)

app_name = 'acquiring'
urlpatterns = [
    url(r'user_mode_change/', ChangeModeStateUserViewSet.as_view(), name='paid_courses_role'),
    url(r'course_mode_change/',CourseModesChange.as_view(), name='course_mode_change'),
    url(r'pay_urfu/', PayUrfuDataViewSet.as_view(), name='pay_urfu'),
    # url(r'paid_course_cus/', PaidCoursesCusViewSet, name='paid_course_cus')
    url(r'^list/', include(router_list.urls)),
]
from django.conf.urls import url, include
from itoo_api.acquiring.views import *

from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'paid_course_cus', PaidCoursesCusViewSet)
app_name = 'acquiring'

urlpatterns = [
    url(r'paid_courses_role/', PaidCoursesRoleViewSet.as_view(), name='paid_courses_role'),
    url(r'course_mode_change/',CourseModesChange.as_view(), name='course_mode_change'),
    router.urls
]
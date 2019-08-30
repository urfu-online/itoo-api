"""
URLS for itoo_api
"""
from django.conf.urls import url, include
from django.conf import settings
from itoo_api.v0.views import PaidCoursesRoleViewSet, CourseModesChange

app_name = 'itoo_api'  # pylint: disable=invalid-name
urlpatterns = [
    url(r'^v0/', include('itoo_api.v0.urls')),
    url(r'^v0/', include('organizations.v0.urls')),
    url(r'^v0/paid_courses_role/', PaidCoursesRoleViewSet.as_view(), name='paid_courses_role'),
    url(r'^v0/course_mode_change/{course_id_get}/', CourseModesChange.as_view(), name='course_mode_change')
#     .format(
    #         username=settings.USERNAME_PATTERN, course_key=settings.COURSE_ID_PATTERN)
]

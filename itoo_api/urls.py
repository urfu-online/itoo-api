"""
URLS for itoo_api
"""
from django.conf.urls import url, include
from django.conf import settings
from itoo_api.v0.views import PaidCoursesRoleViewSet

app_name = 'itoo_api'  # pylint: disable=invalid-name
urlpatterns = [
    url(r'^v0/', include('itoo_api.v0.urls')),
    url(r'^v0/', include('organizations.v0.urls')),
    url(r'^v0/paid_courses_role/{username},{course_key}$'.format(
        username=settings.USERNAME_PATTERN, course_key=settings.COURSE_ID_PATTERN), PaidCoursesRoleViewSet.as_view(), name='paid_courses_role'),
]

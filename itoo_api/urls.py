"""
URLS for itoo_api
"""
from django.conf.urls import url, include
# from django.conf import settings

app_name = 'itoo_api'  # pylint: disable=invalid-name
urlpatterns = [
    url(r'^v0/', include('itoo_api.v0.urls')),
    url(r'^acquiring/', include('itoo_api.acquiring.urls')),
    url(r'^verified_profile/', include('itoo_api.verified_profile.urls', namespace='verified_profile')),
    url('r^reflection/', include('itoo_api.reflection.urls', namespace='reflection')),
    url(r'^v0/', include('organizations.v0.urls')),
    # url(r'^v0/course_mode_change/(?P<course_id_get>[^/.]+)/', CourseModesChange.as_view(), name='course_mode_change')
#     .format(
    #         username=settings.USERNAME_PATTERN, course_key=settings.COURSE_ID_PATTERN)
]

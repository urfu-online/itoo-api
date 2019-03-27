"""
URLS for itoo_api end points.
"""
# pylint: disable=invalid-name
from rest_framework import routers
from django.conf import settings

from itoo_api.v0.views import ProgramViewSet, OrganizationViewSet, ProgramCourseViewSet, EnrollmentViewSet

router = routers.SimpleRouter()
router.register(r'programs', ProgramViewSet)
router.register(r'link_courses', ProgramCourseViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'enrollment/{course_key}$'.format(course_key=settings.COURSE_ID_PATTERN), EnrollmentViewSet, base_name='enrollment')

app_name = 'v0'
urlpatterns = router.urls

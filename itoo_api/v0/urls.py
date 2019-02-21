"""
URLS for itoo_api end points.
"""
# pylint: disable=invalid-name
from rest_framework import routers

from itoo_api.v0.views import ProgramViewSet, OrganizationViewSet, ProgramCourseViewSet, EnrollmentViewSet

router = routers.SimpleRouter()
router.register(r'programs', ProgramViewSet)
router.register(r'link_courses', ProgramCourseViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'enrollment', EnrollmentViewSet)

app_name = 'v0'
urlpatterns = router.urls

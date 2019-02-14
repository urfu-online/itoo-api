"""
URLS for itoo_api end points.
"""
# pylint: disable=invalid-name
from rest_framework import routers

from itoo_api.v0.views import ProgramViewSet, OrganizationViewSet, ProgramCourseViewSet

router = routers.SimpleRouter()
router.register(r'programs', ProgramViewSet)
router.register(r'programs/courses', ProgramCourseViewSet)
router.register(r'organizations', OrganizationViewSet)

app_name = 'v0'
urlpatterns = router.urls

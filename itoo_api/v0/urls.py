"""
URLS for itoo_api end points.
"""
# pylint: disable=invalid-name
from rest_framework import routers

from itoo_api.v0.views import ProgramViewSet

router = routers.SimpleRouter()
router.register(r'itoo_api', ProgramViewSet)

app_name = 'v0'
urlpatterns = router.urls

"""
URLS for itoo_api
"""
from django.conf.urls import url, include

app_name = 'itoo_api'  # pylint: disable=invalid-name
urlpatterns = [
    url(r'^v0/', include('itoo_api.v0.urls')),
]

"""
itoo-api app initialization module
"""

# from verified_profile.models import Offer, Profile

__version__ = '0.0.1'  # pragma: no cover

default_app_config = 'itoo_api.apps.ItooApiConfig'
try:
    import itoo_api.auto_cohorting.apps  # noqa
except ImportError:
    pass
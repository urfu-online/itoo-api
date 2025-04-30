from django.apps import AppConfig

class AutoCohortingConfig(AppConfig):
    name = 'itoo_api.auto_cohorting'

    def ready(self):
        import itoo_api.auto_cohorting.signals  # noqa
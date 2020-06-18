from django.core.management.base import BaseCommand

from itoo_api.acquiring.views import check_payment_status


class Command(BaseCommand):
    def handle(self, *args, **options):
        output = check_payment_status()

        return output

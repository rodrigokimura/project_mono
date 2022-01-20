from django.core.management.base import BaseCommand, CommandError

from ...report import Report


class Command(BaseCommand):
    help = 'Send report to admins'

    def handle(self, *args, **options):
        try:
            print("Sending report...")
            Report().send()
        except Exception as e:
            raise CommandError(repr(e))

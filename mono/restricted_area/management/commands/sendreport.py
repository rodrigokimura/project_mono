"""Command to send report to the project's mailing list."""
from django.core.management.base import BaseCommand, CommandError

from ...report import Report


class Command(BaseCommand):
    help = "Send report to admins"

    def handle(self, *args, **options):
        try:
            Report().send()
        except Exception as any_exception:  # pylint: disable=broad-except
            raise CommandError(repr(any_exception)) from any_exception

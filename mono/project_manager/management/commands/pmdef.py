from django.core.management.base import BaseCommand, CommandError
from project_manager.models import Theme, Icon


class Command(BaseCommand):
    help = 'Command to prepopulate database'

    def handle(self, *args, **options):
        try:
            Theme._create_defaults()
            Icon._create_defaults()

        except Exception as e:
            CommandError(repr(e))

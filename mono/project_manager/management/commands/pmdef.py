from django.core.management.base import BaseCommand, CommandError
from project_manager.models import Theme, Icon


class Command(BaseCommand):
    help = 'Command to prepopulate database'

    def handle(self, *args, **options):
        try:
            Theme._create_defaults()
            # Icon._create_defaults()
            icons_file = open('icons.txt', 'r')
            for line in icons_file.readlines():
                if line.strip() != '':
                    Icon.objects.update_or_create(markup=line)

        except Exception as e:
            CommandError(repr(e))

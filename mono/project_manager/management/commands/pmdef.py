import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from project_manager.models import Theme, Icon


class Command(BaseCommand):
    help = 'Command to prepopulate database'

    def handle(self, *args, **options):
        try:
            Theme._create_defaults()
            # Icon._create_defaults()
            print('ok')
            path = os.path.join(
                settings.BASE_DIR,
                'project_manager',
                'management',
                'commands'
            )
            print(path)
            icons_file = open(os.path.join(path, 'icons.txt'), 'r')
            print(icons_file)
            for line in icons_file.readlines():
                print(line)
                if line.strip() != '':
                    Icon.objects.update_or_create(markup=line.strip())

        except Exception as e:
            CommandError(repr(e))

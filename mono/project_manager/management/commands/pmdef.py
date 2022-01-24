"""Command to prepopulate database"""
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from project_manager.models import Icon, Theme


class Command(BaseCommand):
    help = 'Command to prepopulate database'

    def handle(self, *args, **options):
        """Command to prepopulate database"""
        try:
            Theme.create_defaults()
            # Icon.create_defaults()
            print('ok')
            path = os.path.join(
                settings.BASE_DIR,
                'project_manager',
                'management',
                'commands'
            )
            with open(os.path.join(path, 'icons.txt'), encoding='utf-8', mode='r') as icons_file:
                for line in icons_file.readlines():
                    if line.strip() != '':
                        Icon.objects.update_or_create(markup=line.strip())

        except Exception as any_exception:  # pylint: disable=broad-except
            raise CommandError(repr(any_exception)) from any_exception

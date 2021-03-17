from django.core.management.base import BaseCommand, CommandError
from pathlib import Path


class Command(BaseCommand):
    help = 'Command to reload the app'
        
    def handle(self, *args, **options):
        try:
            Path('/var/www/www_monoproject_info_wsgi.py').touch()
            print("I'm working.")
        except Exception as e:
            CommandError(repr(e))
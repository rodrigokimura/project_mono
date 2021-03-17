from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import mail_admins
from django.template.loader import get_template
from pathlib import Path
from django.utils import timezone

class Command(BaseCommand):
    help = 'Command to reload the app'
        
    def handle(self, *args, **options):
        try:
            wsgi_file = '/var/www/www_monoproject_info_wsgi.py'

            # TODO: #102 Check for migrations to apply before reloading
            # TODO: #103 Check for new static files to apply before reloading

            Path(wsgi_file).touch()
            print(f"{wsgi_file} has been touched.")

            d = {
                'title': 'Merged PR',
                'warning_message': f'Deploy',
                'first_line': 'Project Mono app has been reloaded.',
                'main_text_lines': [
                    # f'Migrations: {}',
                    f'Deployed at: {timezone.now()}',
                ],
                'button_link': settings.ALLOWED_HOSTS[0],
                'button_text': 'Go to app',
                'after_button': '',
                'unsubscribe_link': None,
            }

            print("Notifying admins about the deployment.")
            mail_admins(
                subject=f'Deploy Notification', 
                message=get_template('email/alert.txt').render(d),
                html_message=get_template('email/alert.html').render(d)
            )

        except Exception as e:
            CommandError(repr(e))
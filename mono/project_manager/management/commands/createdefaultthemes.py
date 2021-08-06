from django.core.management.base import BaseCommand, CommandError
from ...models import Theme


class Command(BaseCommand):
    help = 'Command to create budgets from budget configurations (schedulers)'

    def handle(self, *args, **options):
        try:
            for theme in Theme.DEFAULT_THEMES:
                Theme.objects.update_or_create(
                    name=theme[0],
                    defaults={
                        'primary': theme[1],
                        'secondary': theme[2],
                        'tertiary': theme[3],
                    }
                )

        except Exception as e:
            CommandError(repr(e))

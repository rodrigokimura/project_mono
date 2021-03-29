from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from ...models import User, BudgetConfiguration

class Command(BaseCommand):
    help = 'Command to create budgets from budget configurations (schedulers)'
        
    def handle(self, *args, **options):
        try:
            # Get all budget configs
            configs = BudgetConfiguration.objects.filter(active=True)
            for config in configs:
                config.create()
        except Exception as e:
            CommandError(repr(e))
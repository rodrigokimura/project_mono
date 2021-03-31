from django.core.management.base import BaseCommand, CommandError
from ...models import BudgetConfiguration


class Command(BaseCommand):
    help = 'Command to create budgets from budget configurations (schedulers)'

    def handle(self, *args, **options):
        try:
            # Get all budget configs
            configs = BudgetConfiguration.objects.filter(active=True)
            for config in configs:
                config.create_budget()
        except Exception as e:
            CommandError(repr(e))

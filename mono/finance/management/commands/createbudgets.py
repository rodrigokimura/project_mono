"""Command to create budgets from budget configurations (schedulers)"""
from django.core.management.base import BaseCommand, CommandError

from ...models import BudgetConfiguration


class Command(BaseCommand):
    help = 'Command to create budgets from budget configurations (schedulers)'

    def handle(self, *args, **options):
        """Command to create budgets from budget configurations (schedulers)"""
        try:
            configs = BudgetConfiguration.objects.filter(active=True)
            for config in configs:
                config.create_budget()
        except Exception as any_exception:  # pylint: disable=broad-except
            raise CommandError(repr(any_exception)) from any_exception

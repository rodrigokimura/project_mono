"""Command to create recurrent transactions"""
from django.core.management.base import BaseCommand, CommandError

from ...models import RecurrentTransaction


class Command(BaseCommand):
    help = 'Command to create recurrent transactions'

    def handle(self, *args, **options):
        """Command to create recurrent transactions"""
        try:
            # Get all Recurrent Transactions
            recurrent_transactions = RecurrentTransaction.objects.filter(active=True)
            for recurrent_transaction in recurrent_transactions:
                recurrent_transaction.create_transaction()
        except Exception as any_exception:  # pylint: disable=broad-except
            raise CommandError(repr(any_exception)) from any_exception

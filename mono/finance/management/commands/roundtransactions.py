"""Command to round all transactions"""
from django.core.management.base import BaseCommand, CommandError

from ...models import Transaction


class Command(BaseCommand):
    help = 'Command to round all transactions'

    def handle(self, *args, **options):
        try:
            print("Rounding transactions...")
            qs = Transaction.objects.all()
            for transaction in qs:
                transaction.round_amount()
                transaction.save()
            print(f"{qs.count()} transactions rounded.")
        except Exception as any_exception:  # pylint: disable=broad-except
            raise CommandError(repr(any_exception)) from any_exception

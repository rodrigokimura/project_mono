from django.core.management.base import BaseCommand, CommandError

from ...models import RecurrentTransaction


class Command(BaseCommand):
    help = 'Command to create recurrent transactions'

    def handle(self, *args, **options):
        try:
            # Get all Recurrent Transactions
            configs = RecurrentTransaction.objects.filter(active=True)
            for config in configs:
                config.create_transaction()
        except Exception as e:
            raise CommandError(repr(e))

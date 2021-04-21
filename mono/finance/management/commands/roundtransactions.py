from django.core.management.base import BaseCommand, CommandError
from ...models import Transaction


class Command(BaseCommand):
    help = 'Command to round all transactions'

    def handle(self, *args, **options):
        try:
            qs = Transaction.objects.all()
            for t in qs:
                t.amount = round(t.amount, 2)
                t.save()
        except Exception as e:
            CommandError(repr(e))

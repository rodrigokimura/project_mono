from django.core.management.base import BaseCommand, CommandError

from ...models import Transaction


class Command(BaseCommand):
    help = 'Command to round all transactions'

    def handle(self, *args, **options):
        try:
            print("Rounding transactions...")
            qs = Transaction.objects.all()
            for t in qs:
                print(t.amount)
                t.round_amount()
                t.save()
            print(f"{qs.count()} transactions rounded.")
        except Exception as e:
            CommandError(repr(e))

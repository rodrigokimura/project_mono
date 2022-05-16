"""Command to create budgets from budget configurations (schedulers)"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ...models import Task
from ...tasks import remind


class Command(BaseCommand):
    help = 'Command to create notification for task reminders'

    def handle(self, *args, **options):
        """Command to create notification for task reminders"""
        try:
            self.stdout.write(f"Current timestamp: {timezone.now()}")
            tasks = Task.objects.filter(
                reminder__range=[
                    timezone.now(),
                    timezone.now() + timezone.timedelta(hours=1),
                ],
                reminded=False,
            )
            self.stdout.write(f"Tasks found: {tasks.count()}")
            for task in tasks:
                remind(task.id, schedule=task.reminder)
        except Exception as any_exception:  # pylint: disable=broad-except
            raise CommandError(repr(any_exception)) from any_exception

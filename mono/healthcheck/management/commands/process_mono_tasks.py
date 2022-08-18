"""Override background_task's process_tasks command to change logging configs"""
import logging

from background_task.management.commands.process_tasks import (
    Command as BaseCommand,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        return super().handle(*args, **options)

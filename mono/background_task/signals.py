"""Signals for background tasks"""
import django.dispatch
from background_task.settings import app_settings
from django.db import connections

task_created = django.dispatch.Signal()
task_error = django.dispatch.Signal()
task_rescheduled = django.dispatch.Signal()
task_failed = django.dispatch.Signal()
task_successful = django.dispatch.Signal()
task_started = django.dispatch.Signal()
task_finished = django.dispatch.Signal()


def reset_queries(**kwargs):
    """Register an event to reset saved queries when a Task is started."""
    if app_settings.BACKGROUND_TASK_RUN_ASYNC:
        for conn in connections.all():
            conn.queries_log.clear()


task_started.connect(reset_queries)


def close_old_connections(**kwargs):
    """
    Register an event to reset transaction state and close connections past
    their lifetime.
    """
    if app_settings.BACKGROUND_TASK_RUN_ASYNC:
        for conn in connections.all():
            conn.close_if_unusable_or_obsolete()


task_started.connect(close_old_connections)
task_finished.connect(close_old_connections)

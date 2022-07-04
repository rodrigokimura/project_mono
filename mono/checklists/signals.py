"""Checklists signals"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Task

# pylint: disable=unused-argument


@receiver(pre_save, sender=Task, dispatch_uid="schedule_reminder")
def schedule_reminder(sender, instance: Task, **kwargs):
    """Call async task for reminder"""
    if instance.id is None:
        instance.schedule_reminder()
    else:
        previous: Task = Task.objects.get(id=instance.id)
        if previous.reminder != instance.reminder:
            instance.schedule_reminder()


@receiver(post_save, sender=Task, dispatch_uid="schedule_recurrent_task_post_save")
@receiver(pre_save, sender=Task, dispatch_uid="schedule_recurrent_task")
def schedule_recurrent_task(sender, instance: Task, **kwargs):
    """Call async task to create recurrent task"""
    if 'created' in kwargs:  # post_save
        if kwargs['created']:
            instance.schedule_recurrent_task()
    elif instance.id is not None:
        previous: Task = Task.objects.get(id=instance.id)
        if (
            previous.recurrence != instance.recurrence or previous.due_date != instance.due_date
        ):
            instance.schedule_recurrent_task()

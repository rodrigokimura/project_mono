from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Task


@receiver(pre_save, sender=Task, dispatch_uid="schedule_reminder")
def schedule_reminder(sender, instance: Task, **kwargs):
    if instance.id is None:
        instance.schedule_reminder()
    else:
        previous = Task.objects.get(id=instance.id)
        if previous.reminder != instance.reminder:
            instance.schedule_reminder()

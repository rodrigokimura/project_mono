from .models import TimeEntry


def calculate_duration(sender, instance, **kwargs):
    if sender == TimeEntry:
        if instance.stopped_at is not None:
            instance.duration = instance.stopped_at - instance.started_at

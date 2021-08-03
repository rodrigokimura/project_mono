from .models import Board, Bucket, TimeEntry


def calculate_duration(sender, instance, **kwargs):
    if sender == TimeEntry:
        if instance.stopped_at is not None:
            instance.duration = instance.stopped_at - instance.started_at


def create_default_buckets(sender, instance, created, **kwargs):
    if sender == Board and created:
        for name, desc, order in Bucket.DEFAULT_BUCKETS:
            Bucket.objects.create(
                name=name,
                description=desc,
                order=order,
                created_by=instance.created_by,
                board=instance,
            )

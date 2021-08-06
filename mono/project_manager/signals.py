from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .models import Board, Bucket, TimeEntry


@receiver(pre_save, sender=TimeEntry, dispatch_uid="calculate_duration")
def calculate_duration(sender, instance, **kwargs):
    if sender == TimeEntry:
        if instance.stopped_at is not None:
            instance.duration = instance.stopped_at - instance.started_at


@receiver(post_save, sender=Board, dispatch_uid="create_default_buckets")
def create_default_buckets(sender, instance, created, **kwargs):
    if sender == Board and created:
        for name, desc, order, auto_status in Bucket.DEFAULT_BUCKETS:
            Bucket.objects.create(
                name=name,
                description=desc,
                order=order,
                created_by=instance.created_by,
                board=instance,
                auto_status=auto_status,
            )
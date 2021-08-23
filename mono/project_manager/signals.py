from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .models import Board, Bucket, Comment, TimeEntry, Invite


@receiver(pre_save, sender=TimeEntry, dispatch_uid="calculate_duration")
def calculate_duration(sender, instance, **kwargs):
    if instance.stopped_at is not None:
        instance.duration = instance.stopped_at - instance.started_at


@receiver(post_save, sender=Board, dispatch_uid="create_default_buckets")
def create_default_buckets(sender, instance, created, **kwargs):
    if created:
        for name, desc, order, auto_status in Bucket.DEFAULT_BUCKETS:
            Bucket.objects.create(
                name=name,
                description=desc,
                order=order,
                created_by=instance.created_by,
                board=instance,
                auto_status=auto_status,
            )


@receiver(post_save, sender=Invite, dispatch_uid="send_project_invite")
def send_invite(sender, instance, created, **kwargs):
    if instance.email is not None:
        instance.send()


@receiver(post_save, sender=Comment, dispatch_uid="send_email_on_comment")
def send_email_on_comment(sender, instance, created, **kwargs):
    if created:
        print(instance.mentioned_users)
        instance.notify_assignees()
        instance.notify_mentioned_users()

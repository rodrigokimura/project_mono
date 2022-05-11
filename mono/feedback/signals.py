"""Feedback's signals"""
import logging
import os

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Feedback


@receiver(post_save, sender=Feedback, dispatch_uid="send_feedback_to_admins")
def send_feedback_to_admins(sender, instance, created, **kwargs):  # pylint: disable=unused-argument
    """
    Send feedbacks to admins
    """
    if created:
        instance.notify_admins()

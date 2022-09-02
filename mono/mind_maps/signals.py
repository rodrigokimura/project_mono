"""Mind maps signals"""
import logging
import os

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MindMap, Node


@receiver(post_save, sender=MindMap, dispatch_uid="create_default_node")
def create_default(
    sender, instance: MindMap, created, **kwargs
):  # pylint: disable=unused-argument
    """
    Create default node on mind map creation
    """
    if created:
        Node.objects.create(
            name=instance.name,
            mind_map=instance,
            created_by=instance.created_by,
        )

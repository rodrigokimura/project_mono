"""Mind maps signals"""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import MindMap, Node


@receiver(post_save, sender=MindMap, dispatch_uid="create_default_node")
def create_default_node(
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


@receiver(
    post_delete, sender=Node, dispatch_uid="create_default_node_post_delete"
)
def create_default_node_post_delete(
    sender, instance: Node, **kwargs
):  # pylint: disable=unused-argument
    """
    Create default node on mind map creation
    """
    if not MindMap.objects.filter(id=instance.mind_map.id).exists():
        Node.objects.create(
            name=instance.name,
            mind_map=instance.mind_map,
            created_by=instance.created_by,
        )

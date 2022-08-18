"""Shipper's signals"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Ship


@receiver(post_save, sender=Ship, dispatch_uid="generate_portmanteaus")
def generate_portmanteaus(
    sender, instance: Ship, created, **kwargs
):  # pylint: disable=unused-argument
    """
    Create portmanteau instances when ship is created
    """
    if created:
        instance.generate_portmanteaus()

"""Pixel's signals"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Site


@receiver(
    post_save, sender=get_user_model(), dispatch_uid="create_first_pixel_site"
)
def create_first_pixel_site(sender, instance, created, **kwargs):
    """Create first Pixel site on superuser creation"""
    if created and sender == get_user_model():
        if instance.is_superuser:
            Site.objects.get_or_create(
                host=settings.SITE.split("://", 1)[-1],
                defaults={"created_by": instance},
            )

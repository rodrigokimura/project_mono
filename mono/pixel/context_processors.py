"""Pixel's context processors"""
from django.conf import settings

from .models import Site


def site(request):
    """Allow Pixel app to track itself"""
    self_site = Site.objects.filter(
        host=settings.SITE.split('://', 1)[-1],
        created_by__is_superuser=True
    )
    if self_site.exists():
        return {'SELF_SITE': self_site.first()}
    return {'SELF_SITE': None}

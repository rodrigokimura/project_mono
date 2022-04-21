"""Pixel's context processors"""
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Site


def site(request):
    self_site = Site.objects.filter(host=settings.SITE, created_by__is_superuser=True)
    if self_site.exists():
        return {'SELF_SITE': self_site.first()}
    return {'SELF_SITE': None}

"""Shared tamplate tags"""
from django import template
from django.conf import settings

register = template.Library()


@register.filter
def default_image(image):
    """Fallback to default image"""
    try:
        if image.storage.exists(image.name):
            return image.url
    except ValueError:
        pass
    return settings.STATIC_URL + 'image/avatar.svg'

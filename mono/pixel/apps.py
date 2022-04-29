"""Pixel app"""
from __mono.utils import load_signals
from django.apps import AppConfig


class PixelConfig(AppConfig):
    """Pixel App Config"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pixel'

    def ready(self):
        load_signals('pixel')

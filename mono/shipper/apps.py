"""Shipper's app"""
from __mono.utils import load_signals
from django.apps import AppConfig


class ShipperConfig(AppConfig):
    """Shipper's app config"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "shipper"

    def ready(self):
        load_signals(self.name)

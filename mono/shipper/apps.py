"""Shipper's app"""
import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)

class ShipperConfig(AppConfig):
    """Shipper app config"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shipper'

    def ready(self):
        from shipper import signals  # pylint: disable=C0415
        logger.info('Loading signals from %s', signals.__name__)

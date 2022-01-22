"""Project manager's app"""
import logging

from django.apps import AppConfig


logger = logging.getLogger(__name__)

class ProjectManagerConfig(AppConfig):
    """Project manager app config"""
    name = 'project_manager'

    def ready(self):
        from project_manager import signals  # pylint: disable=C0415
        logger.info('Loading signals from %s', signals.__name__)

"""Project manager's app"""
from __mono.utils import load_signals
from django.apps import AppConfig


class ProjectManagerConfig(AppConfig):
    """Project manager's app config"""

    name = "project_manager"

    def ready(self):
        load_signals(self.name)

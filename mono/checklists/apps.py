"""Checklists app"""
from __mono.utils import load_signals
from django.apps import AppConfig


class TodoListsConfig(AppConfig):
    """Checklists app config"""

    name = "checklists"

    def ready(self):
        load_signals("checklists")

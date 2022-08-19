"""Finance's app"""
from __mono.utils import load_signals
from django.apps import AppConfig


class FinanceConfig(AppConfig):
    """Finance's app config"""

    name = "finance"

    def ready(self):
        load_signals(self.name)

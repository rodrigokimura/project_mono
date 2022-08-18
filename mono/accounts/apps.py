"""Accounts' app"""
from __mono.utils import load_signals
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Accounts' app config"""

    name = "accounts"

    def ready(self):
        load_signals("accounts")

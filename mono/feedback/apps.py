"""Feedback's app"""
from __mono.utils import load_signals
from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    """
    Config for feedback app
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "feedback"

    def ready(self):
        load_signals("feedback")

from __mono.utils import load_signals
from django.apps import AppConfig


class BackgroundTasksAppConfig(AppConfig):
    """App config for background tasks"""

    default_auto_field = "django.db.models.AutoField"
    name = "background_task"
    verbose_name = "Background Tasks"

    def ready(self):
        load_signals(self.name)

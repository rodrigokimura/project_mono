from django.apps import AppConfig
from django.db.models.signals import pre_save


class ProjectManagerConfig(AppConfig):
    name = 'project_manager'

    def ready(self):
        from project_manager.models import TimeEntry
        from project_manager.signals import calculate_duration
        pre_save.connect(calculate_duration, sender=TimeEntry, dispatch_uid="calculate_duration")

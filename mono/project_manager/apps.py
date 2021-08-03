from django.apps import AppConfig
from django.db.models.signals import post_save, pre_save


class ProjectManagerConfig(AppConfig):
    name = 'project_manager'

    def ready(self):
        from project_manager.models import TimeEntry, Board
        from project_manager.signals import calculate_duration, create_default_buckets
        pre_save.connect(calculate_duration, sender=TimeEntry, dispatch_uid="calculate_duration")
        post_save.connect(create_default_buckets, sender=Board, dispatch_uid="create_default_buckets")

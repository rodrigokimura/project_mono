from django.apps import AppConfig


class ProjectManagerConfig(AppConfig):
    name = 'project_manager'

    def ready(self):
        from project_manager import signals
        signals.__name__

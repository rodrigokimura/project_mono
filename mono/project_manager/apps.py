from django.apps import AppConfig


class ProjectManagerConfig(AppConfig):
    name = 'project_manager'

    def ready(self):
        import project_manager.signals
        print(f'Connecting signals from: {project_manager.signals.__name__}')

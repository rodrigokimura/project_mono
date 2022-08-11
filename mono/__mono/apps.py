"""Override admin configuration."""
from django.contrib.admin.apps import AdminConfig
from firebase_admin import credentials, initialize_app


class MyAdminConfig(AdminConfig):
    default_site = '__mono.admin.MyAdminSite'

    def ready(self) -> None:
        from django.conf import settings
        if settings.FIREBASE_AUTH_FILE.exists():
            cred = credentials.Certificate(str(settings.FIREBASE_AUTH_FILE))
            initialize_app(cred)
        return super().ready()

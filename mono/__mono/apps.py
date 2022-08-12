"""Override admin configuration."""
from django.contrib.admin.apps import AdminConfig


class MyAdminConfig(AdminConfig):
    default_site = '__mono.admin.MyAdminSite'

"""Django admin config for Watcher"""
from django.contrib import admin

from . import models


@admin.register(models.MindMap)
class MindMapAdmin(admin.ModelAdmin):
    """
    Config for mind maps
    """

    list_display = [
        "id",
        "name",
        "created_by",
        "created_at",
    ]
    list_filter = [
        "name",
        "created_by",
        "created_at",
    ]


@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin):
    """
    Config for nodes
    """

    list_display = [
        "id",
        "name",
        "mind_map",
        "parent",
        "x",
        "y",
        "created_by",
        "created_at",
    ]
    list_filter = [
        "name",
        "created_by",
        "created_at",
    ]

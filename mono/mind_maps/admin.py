"""Django admin config for Watcher"""
from typing import Iterable

from django.contrib import admin

from . import models


@admin.register(models.MindMap)
class MindMapAdmin(admin.ModelAdmin):
    """
    Config for mind maps
    """

    def copy(self, request, queryset: Iterable[models.MindMap]):
        for mind_map in queryset:
            mind_map.copy()

    copy.short_description = "Copy mind map"

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
    actions = [copy]


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

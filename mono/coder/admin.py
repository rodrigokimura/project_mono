"""Coder's admin"""
from django.contrib import admin

from . import models


@admin.register(models.Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'language',
        'created_by',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'title',
        'language',
        'created_by',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'title',
        'language',
    )


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'created_by',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'name',
        'color',
        'created_by',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'name',
        'color',
    )

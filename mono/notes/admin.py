"""Notes' admin"""
from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from . import models

admin.site.register(models.Tag)

@admin.register(models.Note)
class NoteAdmin(MarkdownxModelAdmin):
    list_display = (
        'id',
        'location',
        'title',
        'created_by',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'created_by',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'location',
        'title',
    )

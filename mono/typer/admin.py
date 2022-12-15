"""Django admin config for Typer"""

from django.contrib import admin

from . import models


@admin.register(models.Lesson)
class LessonAdmin(admin.ModelAdmin):
    """
    Config for lessons
    """

    list_display = [
        "id",
        "created_by",
        "created_at",
        "updated_at",
        "name",
    ]
    list_filter = [
        "name",
        "created_by",
        "created_at",
    ]


@admin.register(models.Record)
class RecordAdmin(admin.ModelAdmin):
    """
    Config for records
    """

    list_display = [
        "id",
        "created_by",
        "created_at",
        "lesson",
        "number",
    ]
    list_filter = [
        "lesson",
        "created_by",
        "created_at",
    ]


@admin.register(models.KeyPress)
class KeyPressAdmin(admin.ModelAdmin):
    """
    Config for key presses
    """

    list_display = [
        "id",
        "record",
        "character",
        "milliseconds",
    ]
    list_filter = [
        "record",
    ]

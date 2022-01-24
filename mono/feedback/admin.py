"""Feedback's admin"""
from django.contrib import admin

from . import models


@admin.register(models.Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "feeling",
        "public",
    ]
    list_filter = [
        "user",
        "feeling",
        "public",
    ]

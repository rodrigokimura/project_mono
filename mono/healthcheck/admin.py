"""Healthcheck's admin"""
from django.contrib import admin

from . import models

# Register your models here.


@admin.register(models.PullRequest)
class PullRequestAdmin(admin.ModelAdmin):

    list_display = [
        "number",
        "author",
        "commits",
        "additions",
        "deletions",
        "changed_files",
        "merged_at",
        "received_at",
        "pulled_at",
        "deployed_at",
    ]
    list_filter = [
        "author",
    ]

"""Healthcheck's admin"""
from django.contrib import admin

from . import models


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


@admin.register(models.PytestReport)
class PytestReportAdmin(admin.ModelAdmin):

    list_display = [
        "pytest_version",
        "created_at",
    ]
    list_filter = [
        "pytest_version",
        "created_at",
    ]


@admin.register(models.PytestTestResult)
class PytestTestResultAdmin(admin.ModelAdmin):

    list_display = [
        "report",
        "node_id",
        "duration",
        "outcome",
    ]
    list_filter = [
        "outcome",
    ]

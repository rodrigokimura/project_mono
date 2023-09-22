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
        "id",
        "pull_request",
        "pytest_version",
        "created_at",
        "result_count",
        "duration",
    ]
    list_filter = [
        "pull_request",
        "pytest_version",
        "created_at",
    ]


@admin.register(models.PytestResult)
class PytestResultAdmin(admin.ModelAdmin):
    list_display = [
        "report",
        "node_id",
        "duration",
        "outcome",
    ]
    list_filter = [
        "outcome",
    ]
    search_fields = ("node_id",)


@admin.register(models.CoverageReport)
class CoverageReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "pull_request",
        "coverage_version",
        "created_at",
        "result_count",
        "coverage_percentage",
    )
    list_filter = [
        "pull_request",
        "coverage_version",
        "created_at",
    ]


@admin.register(models.CoverageResult)
class CoverageResultAdmin(admin.ModelAdmin):
    list_display = [
        "report",
        "file",
        "covered_lines",
        "missing_lines",
        "excluded_lines",
        "num_statements",
        "coverage_percentage",
    ]
    list_filter = [
        "report",
        "file",
    ]


@admin.register(models.PylintReport)
class PylintReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "pull_request",
        "created_at",
        "score",
        "result_count",
    )
    list_filter = (
        "created_at",
        "pull_request",
    )


@admin.register(models.PylintResult)
class PylintResultAdmin(admin.ModelAdmin):
    list_display = (
        "report",
        "type",
        "module",
        "path",
        "symbol",
        "message",
        "message_id",
    )
    list_filter = (
        "type",
        "symbol",
        "message_id",
    )
    search_fields = (
        "obj",
        "path",
        "symbol",
        "message",
        "message_id",
    )

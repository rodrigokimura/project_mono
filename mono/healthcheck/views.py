"""Healthcheck's views"""
import hmac
import json
import logging
from datetime import datetime
from hashlib import sha1
from typing import Optional

import pytz
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.loader import MigrationLoader
from django.db.models import Count, FloatField, Sum
from django.db.models.expressions import Value
from django.db.models.fields import IntegerField
from django.db.models.functions import Cast, Coalesce
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from markdownx.utils import markdownify
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from .models import CoverageReport, PullRequest, PylintReport, PytestReport
from .serializers import (
    CommitsByDateSerializer,
    PylintReportSerializer,
    ReportSerializer,
)
from .tasks import deploy_app
from .utils import format_to_heatmap, get_commits_by_date, get_commits_context


def is_valid_signature(x_hub_signature, data):
    """
    Check if payload is correctly signed
    """
    private_key = settings.GITHUB_SECRET
    sha_name, signature = x_hub_signature.split("=")
    if sha_name != "sha1":
        return False
    mac = hmac.new(
        force_bytes(private_key), msg=force_bytes(data), digestmod=sha1
    )
    return hmac.compare_digest(
        force_bytes(mac.hexdigest()), force_bytes(signature)
    )


def string_to_localized_datetime(dt_string):
    return pytz.timezone("UTC").localize(
        datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%SZ"), is_dst=None
    )


def healthcheck(request):
    """
    Simple view to output version information and healthcheck status.
    """
    current_pr_number = (
        PullRequest.objects.filter(deployed_at__isnull=False)
        .values("number")
        .latest("number")
        .get("number")
    )
    return JsonResponse(
        {"version": settings.APP_VERSION, "pr": current_pr_number}
    )


@csrf_exempt
def github_webhook(request: HttpRequest):
    """
    This view receives a POST notification from a GitHub webhook
    everytime a Pull Request is successfully merged.
    """
    if request.method == "POST":
        x_hub_signature = request.headers.get("X-Hub-Signature")
        if not is_valid_signature(x_hub_signature, request.body):
            logging.info("Invalid signature.")
            return HttpResponse(status=403)

        event = request.headers.get("X-GitHub-Event")
        if event == "ping":
            logging.info("Ping sent from GitHub.")
            return HttpResponse("pong")

        if event != "pull_request":
            logging.info("Invalid event.")
            return HttpResponse(status=403)

        body: dict = json.loads(request.body.decode("utf-8"))
        pull_request = body.get("pull_request", {})
        if (
            body.get("action") == "closed"
            and pull_request.get("merged_at")
            and pull_request.get("base", {}).get("ref") == "master"
        ):
            PullRequest.objects.update_or_create(
                number=pull_request.get("number"),
                defaults={
                    "author": pull_request.get("user", {}).get("login"),
                    "last_commit_sha": pull_request.get("base", {}).get("sha"),
                    "commits": pull_request.get("commits"),
                    "additions": pull_request.get("additions"),
                    "deletions": pull_request.get("deletions"),
                    "changed_files": pull_request.get("changed_files"),
                    "merged_at": string_to_localized_datetime(
                        pull_request.get("merged_at")
                    ),
                },
            )
    return HttpResponse("ok")


class HealthcheckHomePage(UserPassesTestMixin, TemplateView):
    """
    Healthcheck homepage
    Show a overview of the project.
    Apps, commits, code lines, quality metrics, etc.
    """

    template_name = "healthcheck/home.html"

    def test_func(self):
        return self.request.user.is_superuser


class CommitsFormattedForHeatmapView(UserPassesTestMixin, APIView):
    """Get commit info formatted for heatmap chart"""

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        """
        Get commits by date
        """
        commits_context = get_commits_context()
        return Response(commits_context)


class ShowMigrationsView(UserPassesTestMixin, APIView):
    """
    CBV to list migrations
    """

    def test_func(self) -> Optional[bool]:
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        """
        List migrations
        """
        loader = MigrationLoader(
            connections[DEFAULT_DB_ALIAS], ignore_no_migrations=True
        )
        graph = loader.graph
        app_names = sorted(loader.migrated_apps)
        migrations = {}
        for app_name in app_names:
            apps_migrations = []
            # self.stdout.write(app_name, self.style.MIGRATE_LABEL)
            shown = set()
            for node in graph.leaf_nodes(app_name):
                for plan_node in graph.forwards_plan(node):
                    if plan_node not in shown and plan_node[0] == app_name:
                        # Give it a nice title if it's a squashed one
                        title = plan_node[1]
                        if graph.nodes[plan_node].replaces:
                            title += f" ({len(graph.nodes[plan_node].replaces)} squashed migrations)"
                        apps_migrations.append(
                            (title, plan_node in loader.applied_migrations)
                        )
                        shown.add(plan_node)
            migrations[app_name] = apps_migrations
        return Response(migrations)


class CommitsByDateView(UserPassesTestMixin, APIView):
    """Get commit info by date"""

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        """
        Get commits by date
        """
        serializer = CommitsByDateSerializer(data=request.query_params)
        if serializer.is_valid():
            date = serializer.validated_data["date"]
            commits = get_commits_by_date(date=date)
            return Response(commits)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangelogView(UserPassesTestMixin, APIView):
    """Read changelog markdown file and convert to html"""

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        """
        Read changelog markdown file and convert to html
        """
        changelog_file = settings.CHANGELOG_FILE
        with open(changelog_file, "r", encoding="utf-8") as file:
            file_content = file.read()
        return Response({"success": True, "html": markdownify(file_content)})


class SummaryView(UserPassesTestMixin, APIView):
    """Read changelog markdown file and convert to html"""

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        """
        Read changelog markdown file and convert to html
        """
        from django.db.models import OuterRef, Subquery

        cov = (
            CoverageReport.objects.filter(pull_request=OuterRef("pk"))
            .annotate(
                statements=Sum("results__num_statements")
                + Sum("results__excluded_lines"),
                coverage=Cast(Sum("results__covered_lines"), FloatField())
                / Cast(Sum("results__num_statements"), FloatField()),
            )
            .order_by("-pull_request")
        )

        pylint = (
            PylintReport.objects.filter(pull_request=OuterRef("pk"))
            .annotate(
                issues=Count("results__id"),
            )
            .order_by("-pull_request")
        )

        pytest = (
            PytestReport.objects.filter(pull_request=OuterRef("pk"))
            .annotate(
                tests=Count("results__id"),
                duration=Cast(Sum("results__duration"), FloatField()) / 10e5,
            )
            .order_by("-pull_request")
        )

        pull_requests = PullRequest.objects.annotate(
            cov_statements=Subquery(cov.values("statements")[:1]),
            cov_coverage=Subquery(cov.values("coverage")[:1]),
            pylint_issues=Subquery(pylint.values("issues")[:1]),
            pylint_score=Subquery(pylint.values("score")[:1]),
            pytest_tests=Subquery(pytest.values("tests")[:1]),
            pytest_duration=Subquery(pytest.values("duration")[:1]),
        ).values(
            "number",
            "deployed_at",
            "cov_statements",
            "cov_coverage",
            "pylint_issues",
            "pylint_score",
            "pytest_tests",
            "pytest_duration",
        )
        return Response({"success": True, "results": pull_requests})


class PytestReportViewSet(ViewSet):
    """
    Upload and parse pytest report file
    """

    serializer_class = ReportSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request):
        """Show results of last uploaded and parsed report file"""
        last_report = PytestReport.objects.last()
        if last_report is None:
            results = []
        else:
            results = last_report.results.values(
                "node_id",
                "duration",
                "outcome",
            )
        return Response(
            {
                "success": True,
                "pytest_results": [
                    {**r, **{"duration": r["duration"].total_seconds()}}
                    for r in results
                ],
            }
        )

    def create(self, request):
        """Upload and parse report file"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            report_file = request.FILES.get("report_file")
            pr_number = serializer.validated_data.get("pr_number")
            result = PytestReport.process_file(report_file, pr_number)
            return Response(f"Test results parsed: {len(result)}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CoverageReportViewSet(ViewSet):
    """
    Upload and parse coverage report file
    """

    serializer_class = ReportSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request):
        """Show results of last uploaded and parsed report file"""
        last_report = CoverageReport.objects.last()
        if last_report is None:
            results = []
        else:
            results = last_report.results.values(
                "file",
                "covered_lines",
                "missing_lines",
                "excluded_lines",
                "num_statements",
            )
        return Response({"success": True, "results": results})

    def create(self, request):
        """Upload and parse report file"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            report_file = request.FILES.get("report_file")
            pr_number = serializer.validated_data.get("pr_number")
            result = CoverageReport.process_file(report_file, pr_number)
            return Response(f"Coverage results parsed: {len(result)}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PylintReportViewSet(ViewSet):
    """
    Upload and parse pylint report file
    """

    serializer_class = PylintReportSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request):
        """Show results of last uploaded and parsed report file"""
        last_report: PylintReport = PylintReport.objects.last()
        if last_report is None:
            results = []
        else:
            results = last_report.results.values(
                "type",
                "module",
                "obj",
                "line",
                "column",
                "end_line",
                "end_column",
                "path",
                "symbol",
                "message",
                "message_id",
            )
        return Response(
            {"success": True, "score": last_report.score, "results": results}
        )

    def create(self, request):
        """Upload and parse report file"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            report_file = request.FILES.get("report_file")
            pr_number = serializer.validated_data.get("pr_number")
            score = serializer.validated_data.get("score")
            result = PylintReport.process_file(report_file, score, pr_number)
            return Response(f"Pylint results parsed: {len(result)}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

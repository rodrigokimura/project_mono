"""Healthcheck's views"""
import hmac
import json
import logging
from datetime import datetime
from hashlib import sha1

import pytz
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Sum
from django.db.models.expressions import Value
from django.db.models.fields import IntegerField
from django.db.models.functions.comparison import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from markdownx.utils import markdownify
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from .models import (
    CoverageReport, CoverageResult, PullRequest, PylintReport, PytestReport,
)
from .serializers import CommitsByDateSerializer, ReportSerializer
from .tasks import deploy_app
from .utils import format_to_heatmap, get_commits_by_date, get_commits_context


def is_valid_signature(x_hub_signature, data):
    """
    Check if payload is correctly signed
    """
    private_key = settings.GITHUB_SECRET
    sha_name, signature = x_hub_signature.split('=')
    if sha_name != 'sha1':
        return False
    mac = hmac.new(force_bytes(private_key), msg=force_bytes(data), digestmod=sha1)
    return hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature))


def string_to_localized_datetime(dt_string):
    return pytz.timezone("UTC").localize(
        datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%SZ"),
        is_dst=None
    )


def healthcheck(request):
    current_pr: PullRequest = PullRequest.objects.exclude(deployed_at=None).latest('number')
    return JsonResponse({'build_number': current_pr.build_number})


@csrf_exempt
def github_webhook(request):
    """
    This view receives a POST notification from a GitHub webhook
    everytime a Pull Request is successfully merged.
    """
    if request.method == "POST":
        x_hub_signature = request.headers.get('X-Hub-Signature')
        if not is_valid_signature(x_hub_signature, request.body):
            logging.info("Invalid signature.")
            return HttpResponse(status=403)

        event = request.headers.get('X-GitHub-Event')
        if event == 'ping':
            logging.info("Ping sent from GitHub.")
            return HttpResponse("pong")

        if event != "pull_request":
            logging.info("Invalid event.")
            return HttpResponse(status=403)

        body = json.loads(request.body.decode('utf-8'))
        ref = body['pull_request']['base']['ref']
        if body["action"] == "closed" and body["pull_request"]["merged"] and ref == 'master':
            pull_request = body['pull_request']
            PullRequest.objects.update_or_create(
                number=pull_request["number"],
                defaults={
                    'author': pull_request["user"]['login'],
                    'last_commit_sha': pull_request['base']['sha'],
                    'commits': pull_request["commits"],
                    'additions': pull_request["additions"],
                    'deletions': pull_request["deletions"],
                    'changed_files': pull_request["changed_files"],
                    'merged_at': string_to_localized_datetime(pull_request["merged_at"])
                }
            )
    return HttpResponse("ok")


class Deploy(UserPassesTestMixin, TemplateView):
    """Deploy app"""
    template_name = 'healthcheck/deploy.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['last_pr'] = PullRequest.objects.latest('number')
        pull_requests = PullRequest.objects.all()
        context['pull_requests'] = pull_requests

        def _get_commits_by_date(pull_requests, date):
            return pull_requests.filter(
                merged_at__date=date
            ).aggregate(
                sum=Coalesce(
                    Sum('commits'),
                    Value(0),
                    output_field=IntegerField()
                )
            )['sum']

        context_data = format_to_heatmap(
            pull_requests,
            _get_commits_by_date,
        )
        context = {**context_data, **context}
        return context

    # def get_context_data(self, **kwargs):
    #     def _get_diff_context(diff_index):
    #         for i, d in enumerate(diff_index):
    #             if d.change_type in ['M']:
    #                 try:
    #                     a = d.a_blob.data_stream.read().decode("utf-8").split("\n")
    #                     b = d.b_blob.data_stream.read().decode("utf-8").split("\n")
    #                     human_diff = []
    #                     for line in difflib.context_diff(a, b):
    #                         human_diff.append(line)
    #                     yield (i, d.change_type, d.a_path, human_diff)
    #                 except Exception:
    #                     yield (i, d.change_type, d.a_path, None)
    #             else:
    #                 try:
    #                     if d.a_blob is not None:
    #                         file = d.a_blob.data_stream.read().decode("utf-8").split("\n")
    #                     elif d.b_blob is not None:
    #                         file = d.b_blob.data_stream.read().decode("utf-8").split("\n")
    #                     yield (i, d.change_type, d.a_path, file)
    #                 except Exception:
    #                     yield (i, d.change_type, d.a_path, None)
    #     context = super().get_context_data(**kwargs)
    #     path = Path(settings.BASE_DIR).resolve().parent
    #     repo = git.Repo(path)
    #     local_master = repo.commit("master")
    #     remote_master = repo.commit("origin/master")
    #     diff_index = local_master.diff(remote_master)
    #     context['diff_items'] = _get_diff_context(diff_index)
    #     return context

    def post(self, request):
        """Deploy pull request"""
        pull_request = get_object_or_404(PullRequest, pk=request.POST.get('pk', None))
        deploy_app(pull_request.number)
        return JsonResponse(
            {
                'success': True,
                'message': 'Successfully scheduled deployment.',
                'data': {
                    'number': pull_request.number,
                },
            }
        )


class HealthcheckHomePage(UserPassesTestMixin, TemplateView):
    """
    Healthcheck homepage
    Show a overview of the project.
    Apps, commits, code lines, quality metrics, etc.
    """
    template_name = 'healthcheck/home.html'

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
            date = serializer.validated_data['date']
            commits = get_commits_by_date(date=date)
            return Response(
                [
                    {
                        'hexsha': commit.hexsha,
                        'author': commit.author.name,
                        'date': commit.authored_date,
                        'message': commit.message,
                    }
                    for commit in commits
                ]
            )
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
        with open(changelog_file, 'r') as f:
            md = f.read()
        changelog_html = markdownify(md)
        return Response({
            'success': True,
            'html': changelog_html
        })


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
                'node_id',
                'duration',
                'outcome',
            )
        return Response({
            'success': True,
            'pytest_results': results
        })

    def create(self, request):
        """Upload and parse report file"""
        report_file = request.FILES.get('report_file')
        result = PytestReport.process_file(report_file)
        return Response(f'Test results parsed: {len(result)}')


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
                'file',
                'covered_lines',
                'missing_lines',
                'excluded_lines',
                'num_statements',
            )
        return Response({
            'success': True,
            'results': results
        })

    def create(self, request):
        """Upload and parse report file"""
        report_file = request.FILES.get('report_file')
        result = CoverageReport.process_file(report_file)
        return Response(f'Coverage results parsed: {len(result)}')


class PylintReportViewSet(ViewSet):
    """
    Upload and parse pylint report file
    """
    serializer_class = ReportSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request):
        """Show results of last uploaded and parsed report file"""
        last_report = PylintReport.objects.last()
        if last_report is None:
            results = []
        else:
            results = last_report.results.values(
                'type',
                'module',
                'obj',
                'line',
                'column',
                'end_line',
                'end_column',
                'path',
                'symbol',
                'message',
                'message_id',
            )
        return Response({
            'success': True,
            'results': results
        })

    def create(self, request):
        """Upload and parse report file"""
        report_file = request.FILES.get('report_file')
        result = PylintReport.process_file(report_file)
        return Response(f'Pylint results parsed: {len(result)}')

"""Healthcheck's models."""
import logging
from pathlib import Path

import git
import json
from collections import Counter
from itertools import groupby
from datetime import timedelta
from django.conf import settings
from django.core.mail import mail_admins
from django.core.management import execute_from_command_line
from django.db import models, transaction
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


def is_there_migrations_to_make(app_label, silent=False):
    """Check for migrations to make."""
    # This doesn's work when a third-party app requires migrations
    try:
        if silent:
            execute_from_command_line(
                ["manage.py", "makemigrations", app_label, "--check", "--dry-run", "--verbosity", "0"]
            )
        else:  # pragma: no cover
            execute_from_command_line(
                ["manage.py", "makemigrations", app_label, "--check", "--dry-run", "--verbosity", "3"]
            )
        system_exit = 0
    except SystemExit as system_exit_exception:  # pragma: no cover
        system_exit = system_exit_exception
    return system_exit != 0


class PullRequest(models.Model):
    """Stores pull requests coming from GitHub webhook."""
    number = models.IntegerField(unique=True, help_text="GitHub unique identifier.")
    author = models.CharField(max_length=100, help_text="Login username that triggered the pull request.")
    last_commit_sha = models.CharField(max_length=50, help_text="SHA of the last commit.", null=True, blank=True)
    commits = models.IntegerField(default=0)
    additions = models.IntegerField(default=0)
    deletions = models.IntegerField(default=0)
    changed_files = models.IntegerField(default=0)
    merged_at = models.DateTimeField(null=True, blank=True, default=None)
    received_at = models.DateTimeField(auto_now_add=True)
    pulled_at = models.DateTimeField(null=True, blank=True, default=None, help_text="Set when pull method runs.")
    deployed_at = models.DateTimeField(null=True, blank=True, default=None, help_text="Set when deploy method runs.")
    migrations = models.IntegerField(default=None, null=True, blank=True)

    class Meta:
        verbose_name = 'Pull Request'
        verbose_name_plural = 'Pull Requests'
        get_latest_by = "number"

    def __str__(self) -> str:
        return f'PR #{self.number}'

    @property
    def merged(self):
        return self.merged_at is not None

    @property
    def pulled(self):
        return self.pulled_at is not None

    @property
    def link(self):
        return f'https://github.com/rodrigokimura/project_mono/pull/{self.number}'

    @property
    def deployed(self):
        return self.deployed_at is not None

    @property
    def build_number(self):
        """
        Simple code to identify app version.
        """
        year = self.merged_at.year
        count = PullRequest.objects.filter(number__lte=self.number).values('number').distinct().count()
        return f'{year}.{count}'

    def pull(self):
        """Pulls from remote repository and notifies admins."""
        if not self.pulled:
            if settings.APP_ENV == 'PRD':  # pragma: no cover
                path = Path(settings.BASE_DIR).resolve().parent
                repo = git.Repo(path)
                repo.git.reset('--hard', 'origin/master')
                repo.remotes.origin.pull()
                print("Successfully pulled from remote.")
            self.pulled_at = timezone.now()
            self.save()

        context = {
            'title': 'Merged PR',
            'warning_message': f'Pull Request #{self.number}',
            'first_line': 'Detected merged PR',
            'main_text_lines': [
                f'Merged by: {self.author}',
                f'Merged at: {self.merged_at}',
                f'Commits: {self.commits}',
                f'Additions: {self.additions}',
                f'Deletions: {self.deletions}',
                f'Changed files: {self.changed_files}',
            ],
            'button_link': self.link,
            'button_text': f'Go to Pull Request #{self.number}',
            'after_button': '',
            'unsubscribe_link': None,
        }

        mail_admins(
            subject=f'Delivery Notification - {self}',
            message=get_template('email/alert.txt').render(context),
            html_message=get_template('email/alert.html').render(context),
        )


class PytestReport(models.Model):
    """
    Pytest report
    """

    pytest_version = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Pytest Report")
        verbose_name_plural = _("Pytest Reports")

    def __str__(self):
        return f'Pytest Report #{self.pk}'

    @property
    def result_count(self):
        return self.results.count()

    @property
    def duration(self):
        return self.results.aggregate(duration=models.Sum('duration', output_field=models.DurationField()))['duration']

    @classmethod
    @transaction.atomic
    def process_report_file(cls, report_file):
        lines = report_file.readlines()
        report = cls.objects.create(
            pytest_version=json.loads(lines[0]).get('pytest_version')
        )
        pytest_log_objects = list(filter(lambda d: d.get('$report_type') == 'TestReport', map(json.loads, lines)))
        g = groupby(pytest_log_objects, lambda d: d.pop('nodeid'))
        pytest_results = []
        for nodeid, node_data in g:
            c = Counter()
            outcome = 'passed'
            for row in node_data: 
                r = {'duration': row.get('duration', 0)}
                c.update(r)
                if row.get('outome') == 'failed':
                    outcome = 'failed' 
            pytest_results.append(
                PytestResult(
                    report=report,
                    node_id=nodeid,
                    outcome=outcome,
                    duration=timedelta(seconds=dict(c).get('duration', 0)),
                )
            )
        return PytestResult.objects.bulk_create(pytest_results)


class PytestResult(models.Model):
    """
    Individual test result
    """

    class Outcome(models.TextChoices):
        """Outcome choices"""
        PASSED = 'passed', 'Passed'
        FAILED = 'failed', 'Failed'

    report = models.ForeignKey(PytestReport, on_delete=models.CASCADE, related_name="results")
    node_id = models.CharField(max_length=2000, help_text="Test unique identifier.")
    duration = models.DurationField(help_text="Test duration.")
    outcome = models.CharField(choices=Outcome.choices, max_length=6, help_text="Test outcome.")

    class Meta:
        verbose_name = _("Pytest Result")
        verbose_name_plural = _("Pytest Results")

class CoverageReport(models.Model):
    coverage_version = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Coverage Report")
        verbose_name_plural = _("Coverage Reports")

    def __str__(self):
        return f'Coverage Report #{self.pk}'

    @property
    def result_count(self):
        return self.results.count()

    
    @property
    def coverage_percentage(self):
        try:
            total_covered_lines = self.results.aggregate(total_covered_lines=models.Sum('covered_lines'))['total_covered_lines']
            total_missing_lines = self.results.aggregate(total_missing_lines=models.Sum('missing_lines'))['total_missing_lines']
            return f'{total_covered_lines / (total_covered_lines + total_missing_lines):.1%}'
        except ZeroDivisionError:
            return f'{0.0:.1%}'

    @classmethod
    @transaction.atomic
    def process_file(cls, report_file):
        data = json.loads(report_file.read())
        version = data.get('meta', {}).get('version')
        timestamp = data.get('meta', {}).get('timestamp')
        report = CoverageReport.objects.create(
            coverage_version=version
        )
        files = data.get('files', {})
        results = [
            CoverageResult(
                report=report,
                file=k,
                covered_lines=v.get('summary', {}).get('covered_lines'),
                missing_lines=v.get('summary', {}).get('missing_lines'),
                excluded_lines=v.get('summary', {}).get('excluded_lines'),
                num_statements=v.get('summary', {}).get('num_statements'),
            )
            for k, v in files.items()
        ]
        return CoverageResult.objects.bulk_create(results)


class CoverageResult(models.Model):
    report = models.ForeignKey(CoverageReport, on_delete=models.CASCADE, related_name="results")
    file = models.CharField(max_length=2000, help_text="File name.")
    covered_lines = models.PositiveIntegerField()
    missing_lines = models.PositiveIntegerField()
    excluded_lines = models.PositiveIntegerField()
    num_statements = models.PositiveIntegerField()

    @property
    def coverage_percentage(self):
        try:
            return f'{self.covered_lines / (self.covered_lines + self.missing_lines):.1%}'
        except ZeroDivisionError:
            return f'{0.0:.1%}'

    class Meta:
        verbose_name = _("Coverage Result")
        verbose_name_plural = _("Coverage Results")


class PylintReport(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pylint Report #{self.pk}'

    @property
    def result_count(self):
        return self.results.count()

    class Meta:
        verbose_name = _("Pylint Report")
        verbose_name_plural = _("Pylint Reports")


class PylintResult(models.Model):
    report = models.ForeignKey(PylintReport, on_delete=models.CASCADE, related_name="results")
    type = models.CharField(max_length=50, help_text="File name.")
    module = models.CharField(max_length=1000, help_text="Module name.")
    obj = models.CharField(max_length=1000, help_text="Object within the module (if any).")
    line = models.PositiveIntegerField(null=True, help_text="Line number.")
    column = models.PositiveIntegerField(null=True, help_text="Column number.")
    endLine = models.PositiveIntegerField(null=True, help_text="Line number of the end of the node.")
    endColumn = models.PositiveIntegerField(null=True, help_text="Column number of the end of the node.")
    path = models.CharField(max_length=1000, help_text="Relative path to the file.")
    symbol = models.CharField(max_length=50, help_text="Symbolic name of the message.")
    message = models.CharField(max_length=100, help_text="Text of the message.")
    message_id = models.CharField(max_length=10, help_text="Message code.")

    class Meta:
        verbose_name = _("Pylint Result")
        verbose_name_plural = _("Pylint Results")

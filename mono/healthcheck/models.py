import logging
from pathlib import Path

import git
from django.conf import settings
from django.core.mail import mail_admins
from django.core.management import execute_from_command_line
from django.db import models
from django.template.loader import get_template
from django.utils import timezone

logger = logging.getLogger(__name__)


def is_there_migrations_to_make(app_label, silent=False):
    # This doesn's work when a third-party app requires migrations
    try:
        if silent:
            execute_from_command_line(["manage.py", "makemigrations", app_label, "--check", "--dry-run", "--verbosity", "0"])
        else:
            execute_from_command_line(["manage.py", "makemigrations", app_label, "--check", "--dry-run", "--verbosity", "3"])
        system_exit = 0
    except SystemExit as e:
        system_exit = e
    return system_exit != 0


class PullRequest(models.Model):
    """Stores pull requests coming from GitHub webhook."""
    number = models.IntegerField(unique=True, help_text="GitHub unique identifier.")
    author = models.CharField(max_length=100, help_text="Login username that triggered the pull request.")
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

        d = {
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
            message=get_template('email/alert.txt').render(d),
            html_message=get_template('email/alert.html').render(d)
        )

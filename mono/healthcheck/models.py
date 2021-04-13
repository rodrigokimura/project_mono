from django.db import models
from pathlib import Path
from django.conf import settings
import git
from django.utils import timezone
from django.core.mail import mail_admins
from django.template.loader import get_template
from django.db.migrations.executor import MigrationExecutor
from django.db import connections, DEFAULT_DB_ALIAS
from django.core.management import execute_from_command_line


def is_there_migrations_to_make(app_label):
    # This doesn's work when a third-party app requires migrations
    try:
        execute_from_command_line(["manage.py", "makemigrations", app_label, "--check", "--dry-run", "--verbosity", "3"])
        system_exit = 0
    except SystemExit as e:
        system_exit = e
    return system_exit != 0


def pending_migrations(database=DEFAULT_DB_ALIAS):
    """Returns a list of non applied Migration instances"""
    connection = connections[database]
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return [migration for (migration, backwards) in executor.migration_plan(targets)]


def is_database_synchronized(database=DEFAULT_DB_ALIAS):
    """Returns True if there are no migrations to be applied."""
    return not pending_migrations(database)

# Create your models here.


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

    def __str__(self) -> str:
        return f'PR #{self.number}'

    @property
    def merged(self):
        return self.merged_at is not None

    @property
    def pulled(self):
        return self.pulled_at is not None

    @property
    def deployed(self):
        return self.deployed_at is not None

    @property
    def build_number(self):
        year = self.merged_at.year
        count = PullRequest.objects.filter(number__lte=self.number).values('number').distinct().count()
        return f'{year}.{count}'

    def pull(self, **kwargs):
        """Pulls from remote repository and notifies admins."""
        path = Path(settings.BASE_DIR).resolve().parent
        repo = git.Repo(path)
        origin = repo.remotes.origin
        origin.pull()
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
            'button_link': kwargs['link'],
            'button_text': f'Go to Pull Request #{self.number}',
            'after_button': '',
            'unsubscribe_link': None,
        }

        mail_admins(
            subject=f'Delivery Notification - {self}',
            message=get_template('email/alert.txt').render(d),
            html_message=get_template('email/alert.html').render(d)
        )

    def deploy(self, **kwargs):
        """If in production, reloads the app and notifies admins."""
        try:

            if is_database_synchronized():
                print("All migrations have been applied.")
                migrations = []
            else:
                print("Unapplied migrations found.")
                migrations = pending_migrations()
                execute_from_command_line(["manage.py", "migrate"])
                self.migrations = len(migrations)
                self.save()

            if settings.APP_ENV == 'PRD':
                execute_from_command_line(["cd", "~/project_mono"])
                execute_from_command_line(["pip3.8", "install", "-r", "requirements.txt", "--user"])
                wsgi_file = '/var/www/www_monoproject_info_wsgi.py'
                Path(wsgi_file).touch()
                print(f"{wsgi_file} has been touched.")
                execute_from_command_line(["manage.py", "collectstatic", "--noinput"])

            print(f"Successfully deployed {self}.")
            self.deployed_at = timezone.now()
            self.save()

            if not migrations:
                migrations_text_lines = ['No migrations applied.']
            else:
                migrations_text_lines = [f'Migrations applied ({len(migrations)})']
                migrations_text_lines.extend([f'+ {m.app_label}.{m.name}' for m in migrations])

            main_text_lines = [
                f'Merged by: {self.author}',
                f'Merged at: {self.merged_at}',
                f'Commits: {self.commits}',
                f'Additions: {self.additions}',
                f'Deletions: {self.deletions}',
                f'Changed files: {self.changed_files}',
                '',
                f'Build number: {self.build_number}',
                f'Deployed at: {self.deployed_at}',
                '',
            ]
            main_text_lines.extend(migrations_text_lines)

            d = {
                'title': 'Merged PR',
                'warning_message': f'Deployment Notification - {self}',
                'first_line': f'{self} has been deployed.',
                'main_text_lines': main_text_lines,
                'button_link': settings.ALLOWED_HOSTS[0],
                'button_text': 'Go to app',
                'after_button': '',
                'unsubscribe_link': None,
            }

            print("Notifying admins about the deployment.")
            mail_admins(
                subject='Deploy Notification',
                message=get_template('email/alert.txt').render(d),
                html_message=get_template('email/alert.html').render(d)
            )
        except Exception as e:
            print("An error ocurred during deployment.")
            print(e)

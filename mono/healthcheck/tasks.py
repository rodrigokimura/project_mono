import logging
from pathlib import Path

from background_task import background
from django.conf import settings
from django.core.mail import mail_admins
from django.core.management import execute_from_command_line
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor
from django.template.loader import get_template
from django.utils import timezone

from .models import PullRequest

logger = logging.getLogger(__name__)


def get_pending_migrations(database=DEFAULT_DB_ALIAS):
    """Returns a list of non applied Migration instances"""
    connection = connections[database]
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return [migration for (migration, backwards) in executor.migration_plan(targets)]


def restart_production_app():
    WSGI_FILE = '/var/www/www_monoproject_info_wsgi.py'
    Path(WSGI_FILE).touch()
    logger.info(f"{WSGI_FILE} has been touched.")


@background(schedule=60)
def deploy_app(pull_request_number):
    pr: PullRequest = PullRequest.objects.get(number=pull_request_number)

    # Pull code
    pr.pull()

    # Install dependencies
    execute_from_command_line(["pipenv", "install"])

    # Collect Static files
    if settings.APP_ENV == 'PRD':
        execute_from_command_line(["manage.py", "collectstatic", "--noinput"])

    # Apply migrations
    pending_migrations = get_pending_migrations()
    if pending_migrations:
        logger.info("Unapplied migrations found.")
        execute_from_command_line(["manage.py", "migrate"])
        pr.migrations = len(pending_migrations)
        pr.save()
    else:
        logger.info("All migrations have been applied.")

    # Restart app
    restart_production_app()
    logger.info(f"Successfully deployed {pr}.")
    pr.deployed_at = timezone.now()
    pr.save()

    if not pending_migrations:
        migrations_text_lines = ['No migrations applied.']
    else:
        migrations_text_lines = [f'Migrations applied ({len(pending_migrations)})']
        migrations_text_lines.extend([f'+ {m.app_label}.{m.name}' for m in pending_migrations])

    main_text_lines = [
        f'Merged by: {pr.author}',
        f'Merged at: {pr.merged_at}',
        f'Commits: {pr.commits}',
        f'Additions: {pr.additions}',
        f'Deletions: {pr.deletions}',
        f'Changed files: {pr.changed_files}',
        '',
        f'Build number: {pr.build_number}',
        f'Deployed at: {pr.deployed_at}',
        '',
    ]
    main_text_lines.extend(migrations_text_lines)

    d = {
        'title': 'Merged PR',
        'warning_message': f'Deployment Notification - {pr}',
        'first_line': f'{pr} has been deployed.',
        'main_text_lines': main_text_lines,
        'button_link': settings.ALLOWED_HOSTS[0],
        'button_text': 'Go to app',
        'after_button': '',
        'unsubscribe_link': None,
    }

    logger.info("Notifying admins about the deployment.")
    mail_admins(
        subject='Deploy Notification',
        message=get_template('email/alert.txt').render(d),
        html_message=get_template('email/alert.html').render(d)
    )

"""Healthcheck's tasks"""
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
    return [
        migration for (migration, backwards) in executor.migration_plan(targets)
    ]


def restart_production_app():
    """Restart web server in production"""
    if settings.APP_ENV == "PRD":  # pragma: no cover
        wsgi_file = "/var/www/www_monoproject_info_wsgi.py"
        Path(wsgi_file).touch()
        logger.info("%s has been touched.", wsgi_file)


@background(schedule=30)
def deploy_app(pull_request_number):
    """Script to deploy last version of app"""
    pull_request: PullRequest = PullRequest.objects.get(
        number=pull_request_number
    )

    # Pull code
    pull_request.pull()

    # Install dependencies
    # Collect Static files
    if settings.APP_ENV == "PRD":  # pragma: no cover
        execute_from_command_line(["pipenv", "install"])
        execute_from_command_line(["manage.py", "collectstatic", "--noinput"])

    # Apply migrations
    pending_migrations = get_pending_migrations()
    if pending_migrations:  # pragma: no cover
        logger.info("Unapplied migrations found.")
        execute_from_command_line(["manage.py", "migrate"])
        pull_request.migrations = len(pending_migrations)
        pull_request.save()
        migrations_text_lines = [
            f"Migrations applied ({len(pending_migrations)})"
        ]
        migrations_text_lines.extend(
            [f"+ {m.app_label}.{m.name}" for m in pending_migrations]
        )
    else:
        logger.info("All migrations have been applied.")
        migrations_text_lines = ["No migrations applied."]

    # Restart app
    restart_production_app()
    logger.info("Successfully deployed %s.", pull_request)
    pull_request.deployed_at = timezone.now()
    pull_request.save()

    main_text_lines = [
        f"Merged by: {pull_request.author}",
        f"Merged at: {pull_request.merged_at}",
        f"Commits: {pull_request.commits}",
        f"Additions: {pull_request.additions}",
        f"Deletions: {pull_request.deletions}",
        f"Changed files: {pull_request.changed_files}",
        "",
        f"Build number: {pull_request.build_number}",
        f"Deployed at: {pull_request.deployed_at}",
        "",
    ]
    main_text_lines.extend(migrations_text_lines)

    context = {
        "title": "Merged PR",
        "warning_message": f"Deployment Notification - {pull_request}",
        "first_line": f"{pull_request} has been deployed.",
        "main_text_lines": main_text_lines,
        "button_link": settings.ALLOWED_HOSTS[0],
        "button_text": "Go to app",
        "after_button": "",
        "unsubscribe_link": None,
    }

    logger.info("Notifying admins about the deployment.")
    mail_admins(
        subject="Deploy Notification",
        message=get_template("email/alert.txt").render(context),
        html_message=get_template("email/alert.html").render(context),
    )

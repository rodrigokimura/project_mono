"""
Command to mark a release as deployed.
"""
import logging

import git
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ...models import PullRequest

logger = logging.getLogger(__name__)


def find_last_merge_commit():
    """Find the last merge commit and return its hash."""
    repo = git.Repo(search_parent_directories=True)
    headcommit = repo.head.commit
    while True:
        headcommit = headcommit.parents[0]
        if len(headcommit.parents) != 1:
            break
    return str(headcommit)


class Command(BaseCommand):
    help = "Command to deploy the app based on last pulled PR"

    def handle(self, *args, **options):
        try:
            # repo = git.Repo(search_parent_directories=True)
            # sha = repo.head.object.hexsha
            sha = find_last_merge_commit()
            qs = PullRequest.objects.filter(last_commit_sha=sha)

            if not qs.exists():
                raise PullRequest.DoesNotExist(
                    f"No PR found with this SHA: {sha}"
                )
            if qs.count() > 1:
                raise PullRequest.MultipleObjectsReturned(
                    f"Multiple PRs found with this SHA: {sha}"
                )

            pull_request: PullRequest = qs.latest("number")
            pull_request.pull()
            pull_request.deployed_at = timezone.now()
            pull_request.save()
            logger.info("Successfully deployed %s.", pull_request)

        except Exception as any_exception:
            raise CommandError(repr(any_exception)) from any_exception

"""Deploy manage.py command"""
from django.core.management.base import BaseCommand, CommandError

from ...models import PullRequest
from ...tasks import deploy_app


class Command(BaseCommand):
    help = 'Command to deploy the app based on last pulled PR'

    def handle(self, *args, **options):
        try:
            pull_request: PullRequest = PullRequest.objects.latest('number')
            print(f"Last PR: {pull_request}")
            if not pull_request.deployed:
                deploy_app(pull_request.number)
            else:
                print(f'{pull_request} was already deployed at {pull_request.deployed_at}')
        except Exception as any_exception:
            raise CommandError(repr(any_exception)) from any_exception

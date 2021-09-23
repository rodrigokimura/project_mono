from django.core.management.base import BaseCommand, CommandError
from ...models import PullRequest
from ...tasks import deploy_app


class Command(BaseCommand):
    help = 'Command to deploy the app based on last pulled PR'

    def handle(self, *args, **options):
        try:
            pr: PullRequest = PullRequest.objects.latest('number')
            print(f"Last PR: {pr}")
            if not pr.deployed:
                deploy_app(pr.number)
            else:
                print(f'{pr} was already deployed at {pr.deployed_at}')
        except Exception as e:
            CommandError(repr(e))

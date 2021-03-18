from django.core.management.base import BaseCommand, CommandError
from ...models import PullRequest

class Command(BaseCommand):
    help = 'Command to deploy the app based on last pulled PR'
        
    def handle(self, *args, **options):
        try:
            pr = PullRequest.objects.order_by('-number').first()
            print(f"Last PR: {pr}")

            pr.deploy()
            if not pr.deployed:
                print(pr.deploy())
            else:
                print(f'{pr} was already deployed at {pr.deployed_at}')
        except Exception as e:
            CommandError(repr(e))
from django.db import models
from pathlib import Path
from django.conf import settings
import git
from django.utils import timezone
from django.core.mail import mail_admins
from django.template.loader import get_template

# Create your models here.
class PullRequest(models.Model):
    number = models.IntegerField(unique=True)
    author = models.CharField(max_length=100)
    commits = models.IntegerField(default=0)
    additions = models.IntegerField(default=0)
    deletions = models.IntegerField(default=0)
    changed_files = models.IntegerField(default=0)
    merged_at = models.DateTimeField(null=True, blank=True, default=None)
    received_at = models.DateTimeField(auto_now=True)
    pulled_at = models.DateTimeField(null=True, blank=True, default=None)
    deployed_at = models.DateTimeField(null=True, blank=True, default=None)

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

    def pull(self, **kwargs):
        path = Path(settings.BASE_DIR).resolve().parent
        repo = git.Repo(path)
        origin = repo.remotes.origin
        fetchInfoList = origin.pull()
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

    def deploy(self):
        # TODO: #102 Check for migrations to apply before reloading
        # TODO: #103 Check for new static files to apply before reloading
        try:
            if settings.APP_ENV == 'PRD':
                wsgi_file = '/var/www/www_monoproject_info_wsgi.py'
                Path(wsgi_file).touch()
                print(f"{wsgi_file} has been touched.")
                
            print(f"Successfully deployed {self}.")
            self.deployed_at = timezone.now()
            self.save()

            d = {
                'title': 'Merged PR',
                'warning_message': f'Deployment Notification - {self}',
                'first_line': f'{self} has been deployed.',
                'main_text_lines': [
                    f'Deployed at: {self.deployed_at}',
                ],
                'button_link': settings.ALLOWED_HOSTS[0],
                'button_text': 'Go to app',
                'after_button': '',
                'unsubscribe_link': None,
            }

            print("Notifying admins about the deployment.")
            mail_admins(
                subject=f'Deploy Notification', 
                message=get_template('email/alert.txt').render(d),
                html_message=get_template('email/alert.html').render(d)
            )
            return True
        except Exception as e:
            return e
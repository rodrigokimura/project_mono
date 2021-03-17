from django.db import models

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
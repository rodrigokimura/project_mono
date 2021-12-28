from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class Issue(models.Model):
    hash = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True, default=None)
    resolved_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='resolved_issues'
    )
    ignored_at = models.DateTimeField(null=True, blank=True, default=None)
    ignored_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='ignored_issues'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def resolve(self, user):
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save()

    def unresolve(self):
        self.resolved_at = None
        self.resolved_by = None
        self.save()

    def ignore(self, user):
        self.ignored_at = timezone.now()
        self.ignored_by = user
        self.save()

    def unignore(self):
        self.ignored_at = None
        self.ignored_by = None
        self.save()

    @property
    def resolved(self):
        return self.resolved_at is not None

    @property
    def ignored(self):
        return self.ignored_at is not None

    @property
    def users(self):
        return self.event_set.values('user').distinct()


class Event(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.issue)


class Traceback(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()
    file_name = models.CharField(max_length=1000)
    function_name = models.CharField(max_length=1000)
    line_number = models.PositiveIntegerField()
    code_text = models.JSONField()
    variables = models.JSONField()

    def __str__(self):
        return str(self.issue)

    @property
    def short_file_name(self):
        fn: str = self.file_name
        if 'site-packages/' in fn:
            return fn.split('site-packages/')[-1]
        if 'project_mono/mono/' in fn:
            return fn.split('project_mono/mono/')[-1]
        items = fn.split('/')
        if len(items) > 1:
            return '/'.join(items[len(items) - 2:])
        else:
            return items[-1]

    @property
    def vars(self):
        return self.variables.items()

    class Meta:
        ordering = ['-order']

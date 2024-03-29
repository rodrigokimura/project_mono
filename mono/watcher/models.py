"""Watcher's models"""
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Issue(models.Model):
    """Problem encountered by Watcher"""

    hash = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True, default=None)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="resolved_issues",
    )
    ignored_at = models.DateTimeField(null=True, blank=True, default=None)
    ignored_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ignored_issues",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def resolve(self, user):
        """
        Mark issues as resolved
        """
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save()

    def unresolve(self):
        """
        Mark issue as unresolved
        """
        self.resolved_at = None
        self.resolved_by = None
        self.save()

    def ignore(self, user):
        """
        Mark issue as ignored
        """
        self.ignored_at = timezone.now()
        self.ignored_by = user
        self.save()

    def unignore(self):
        """
        Mark issue as not ignored
        """
        self.ignored_at = None
        self.ignored_by = None
        self.save()

    @property
    def resolved(self):
        return self.resolved_at is not None

    @property
    def ignored(self):
        return self.ignored_at is not None


class Event(models.Model):
    """
    When an issue happens
    """

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.issue)


class Traceback(models.Model):
    """
    Hold information about the traceback
    """

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
        """
        Short version of traceback's filename
        """
        if "site-packages/" in self.file_name:
            return self.file_name.rsplit("site-packages/", maxsplit=1)[-1]
        if "project_mono/mono/" in self.file_name:
            return self.file_name.rsplit("project_mono/mono/", maxsplit=1)[-1]
        items = self.file_name.split("/")
        if len(items) > 1:
            return "/".join(items[len(items) - 2 :])
        return items[-1]

    @property
    def vars(self):
        return self.variables.items()

    class Meta:
        ordering = ["-order"]


class Request(models.Model):
    """
    Hold information about requests for analytics purposes
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    started_at = models.DateTimeField()
    duration = models.DurationField()
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=2000)
    route = models.CharField(
        max_length=2000, null=True, blank=True, help_text="URL pattern"
    )
    url_name = models.CharField(max_length=200, null=True, blank=True)
    app_name = models.CharField(
        max_length=200, default="", blank=True, db_index=True
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, default=None
    )


class Comment(models.Model):
    """
    Comments made by users about an issue
    """

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="issue_comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    class Meta:
        ordering = ["created_at"]

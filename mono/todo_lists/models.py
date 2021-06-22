from django.utils.timezone import now
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class List(models.Model):
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=255)
    order = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_todo_tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    checked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checked_todo_tasks", null=True, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.description

    def mark_as_checked(self, user):
        self.checked_by = user
        self.checked_at = now()
        self.save()

    def mark_as_unchecked(self, user):
        self.checked_by = None
        self.checked_at = None
        self.save()

# class Step

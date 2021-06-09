from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class List(models.Model):
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Item(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    order = models.IntegerField()
    # assigned_to = models.ManyToManyField(User, related_name="assigned_cards")
    # files = models.FileField(upload_to=None, max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_todo_items")
    created_at = models.DateTimeField(auto_now_add=True)
    checked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checked_todo_items")
    checked_at = models.DateTimeField()

    def __str__(self) -> str:
        return self.description

    def mark_as_checked(self):
        pass

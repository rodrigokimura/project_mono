import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

DEFAULT_PANEL_SIZE = 2000


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MindMap(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Node(BaseModel):
    mind_map = models.ForeignKey(MindMap, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    x = models.IntegerField(default=DEFAULT_PANEL_SIZE / 2)
    y = models.IntegerField(default=DEFAULT_PANEL_SIZE / 2)

    def __str__(self):
        return self.name

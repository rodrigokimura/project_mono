import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

DEFAULT_PANEL_SIZE = {
    "height": 240,
    "width": 240,
}


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MindMap(BaseModel):
    name = models.CharField(max_length=255)
    scale = models.FloatField(default=10)

    def __str__(self):
        return self.name

    @property
    def nodes(self):
        return self.node_set.all()


class Node(BaseModel):
    mind_map = models.ForeignKey(MindMap, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=100)
    x = models.IntegerField(default=DEFAULT_PANEL_SIZE["width"] / 2)
    y = models.IntegerField(default=DEFAULT_PANEL_SIZE["height"] / 2)
    font_size = models.IntegerField(default=1)
    padding = models.IntegerField(default=1)
    bold = models.BooleanField(default=False)
    italic = models.BooleanField(default=False)
    underline = models.BooleanField(default=False)
    line_through = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def position(self):
        return [self.x, self.y]

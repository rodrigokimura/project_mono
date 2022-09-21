"""Mind maps models"""
import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

DEFAULT_PANEL_SIZE = {
    "height": 240,
    "width": 240,
}


class BaseModel(models.Model):
    """Base model for Mind Maps app"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MindMap(BaseModel):
    """
    Mind map model
    A group of related nodes
    """

    name = models.CharField(max_length=255)
    scale = models.FloatField(default=10)
    color = models.CharField(max_length=7, default="#000000")

    def __str__(self):
        return self.name

    @property
    def nodes(self):
        return self.node_set.all()


class Node(BaseModel):
    """
    Node model
    An entity that can be linked to other nodes
    """

    mind_map = models.ForeignKey(MindMap, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=100)

    x = models.FloatField(default=DEFAULT_PANEL_SIZE["width"] / 2)
    y = models.FloatField(default=DEFAULT_PANEL_SIZE["height"] / 2)

    font_size = models.FloatField(default=1)
    padding = models.FloatField(default=1)
    border_size = models.FloatField(default=0.3)

    font_color = models.CharField(max_length=7, default="#000000")
    border_color = models.CharField(max_length=7, default="#ffffff")
    background_color = models.CharField(max_length=7, default="#ffffff")

    bold = models.BooleanField(default=False)
    italic = models.BooleanField(default=False)
    underline = models.BooleanField(default=False)
    line_through = models.BooleanField(default=False)

    collapsed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def position(self):
        return [self.x, self.y]

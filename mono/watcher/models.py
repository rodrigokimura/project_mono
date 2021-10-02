import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.aggregates import Avg
from django.utils import timezone


class Error(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.CharField(
        max_length=1024,
        null=True,
        help_text="Host of the URL. Port or userinfo should be ommited. https://en.wikipedia.org/wiki/URL"
    )
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return str(self.id)

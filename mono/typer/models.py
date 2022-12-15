"""Typer models"""
from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return self.name


class Record(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    accuracy = models.FloatField()
    chars_per_minute = models.FloatField()

    class Meta:
        ordering = ["lesson", "number"]

    def __str__(self):
        return f"{self.lesson} #{self.number}"

    def key_presses(self):
        return KeyPress.objects.filter(record=self).order_by("milliseconds")


class KeyPress(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    character = models.CharField(max_length=20)
    milliseconds = models.PositiveIntegerField(db_index=True)
    correct = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.character

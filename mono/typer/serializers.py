"""Typer serializers"""
from rest_framework.serializers import (
    CurrentUserDefault,
    HiddenField,
    ModelSerializer,
)

from .models import Lesson, Record


class LessonSerializer(ModelSerializer):
    """
    Lesson serializer
    """

    created_by = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Lesson
        fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
            "name",
            "text",
        ]
        read_only_fields = [
            "created_by",
            "created_at",
            "updated_at",
        ]


class RecordSerializer(ModelSerializer):
    """
    Record serializer
    """

    created_by = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Record
        fields = [
            "id",
            "lesson",
            "number",
            "created_at",
            "created_by",
        ]
        read_only_fields = [
            "number",
            "created_at",
            "created_by",
        ]

"""Typer serializers"""
from django.db import transaction
from rest_framework.serializers import (
    CurrentUserDefault,
    HiddenField,
    ModelSerializer,
)

from .models import KeyPress, Lesson, Record


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


class KeyPressSerializer(ModelSerializer):
    """
    KeyPress serializer
    """

    class Meta:
        model = KeyPress
        fields = ["character", "milliseconds", "correct"]
        extra_kwargs = {"character": {"trim_whitespace": False}}


class RecordSerializer(ModelSerializer):
    """
    Record serializer
    """

    created_by = HiddenField(default=CurrentUserDefault())
    key_presses = KeyPressSerializer(many=True, write_only=True)

    class Meta:
        model = Record
        fields = [
            "id",
            "lesson",
            "accuracy",
            "chars_per_minute",
            "key_presses",
            "number",
            "created_at",
            "created_by",
        ]
        read_only_fields = [
            "number",
            "created_at",
            "created_by",
        ]

    @transaction.atomic()
    def create(self, validated_data: dict):
        """
        Create a new record
        """
        lesson = validated_data["lesson"]

        record = Record.objects.filter(lesson=lesson).last()
        if record:
            validated_data["number"] = record.number + 1
        else:
            validated_data["number"] = 1
        key_presses = validated_data.pop("key_presses")
        record = super().create(validated_data)
        key_presses = [
            KeyPress(record=record, **key_press) for key_press in key_presses
        ]
        KeyPress.objects.bulk_create(key_presses)
        return record

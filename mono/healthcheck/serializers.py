"""Healthcheck's serializers"""
from rest_framework.serializers import DateField, FileField, Serializer


class CommitsByDateSerializer(Serializer):
    """Serializer to get commits by date."""

    date = DateField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class ReportSerializer(Serializer):
    """Serializer to parse report file"""

    report_file = FileField(max_length=50, allow_empty_file=False)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

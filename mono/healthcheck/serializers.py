"""Healthcheck's serializers"""
from rest_framework.serializers import DateField, Serializer, FileField


class CommitsByDateSerializer(Serializer):
    """Serializer to get commits by date."""
    date = DateField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class PytestReportSerializer(Serializer):
    """Serializer to parse pytest report file"""
    report_file = FileField(max_length=50, allow_empty_file=False)

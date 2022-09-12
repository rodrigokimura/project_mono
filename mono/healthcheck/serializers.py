"""Healthcheck's serializers"""
from rest_framework.serializers import (
    DateField,
    DecimalField,
    FileField,
    IntegerField,
    Serializer,
)


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
    pr_number = IntegerField(min_value=1, required=False)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class PylintReportSerializer(ReportSerializer):
    """Serializer to parse report file"""

    score = DecimalField(
        max_value=10,
        decimal_places=2,
        max_digits=4,
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

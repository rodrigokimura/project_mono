"""Healthcheck's serializers"""
from healthcheck.models import PullRequest
from rest_framework.serializers import (
    DateField,
    DecimalField,
    FileField,
    IntegerField,
    Serializer,
    ValidationError,
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

    def validate_pr_number(self, value):
        if PullRequest.objects.filter(number=value).exists():
            return value
        raise ValidationError("Pull request does not exist")

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

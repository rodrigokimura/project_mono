"""Healthcheck's serializers"""
from rest_framework.serializers import DateField, Serializer


class CommitsByDateSerializer(Serializer):
    """Serializer to get commits by date."""
    date = DateField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

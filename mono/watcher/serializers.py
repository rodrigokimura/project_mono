"""Watcher's serializers"""
from rest_framework import serializers
from rest_framework.serializers import Serializer


class IssueResolverSerializer(Serializer):
    """
    Simple serializer to mark as resolver
    """

    resolved = serializers.BooleanField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

class IssueIgnorerSerializer(Serializer):
    """
    Simple serializer to mark as ignored
    """

    ignored = serializers.BooleanField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

"""Watcher's serializers"""
from accounts.serializers import UserSerializer
from rest_framework.serializers import (
    BooleanField,
    CurrentUserDefault,
    DateTimeField,
    IntegerField,
    ModelSerializer,
    Serializer,
)

from .models import Comment, Issue, Request


class IssueResolverSerializer(Serializer):
    """
    Simple serializer to mark as resolver
    """

    resolved = BooleanField(required=True)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class IssueIgnorerSerializer(Serializer):
    """
    Simple serializer to mark as ignored
    """

    ignored = BooleanField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class CommentSerializer(ModelSerializer):
    """Serializer for comment"""

    created_by = UserSerializer(many=False, default=CurrentUserDefault())

    class Meta:
        model = Comment
        fields = [
            "id",
            "issue",
            "text",
            "created_by",
            "created_at",
        ]
        extra_kwargs = {
            "created_by": {"read_only": True},
            "created_at": {"read_only": True},
        }


class IssueSerializer(ModelSerializer):
    """Serializer for issue"""

    events = IntegerField()
    users = IntegerField()
    first_event = DateTimeField()
    last_event = DateTimeField()

    class Meta:
        model = Issue
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "resolved_at",
            "ignored_at",
            "events",
            "users",
            "first_event",
            "last_event",
        ]
        extra_kwargs = {
            "created_at": {"read_only": True},
            "resolved_at": {"read_only": True},
            "ignored_at": {"read_only": True},
            "events": {"read_only": True},
            "users": {"read_only": True},
            "first_event": {"read_only": True},
            "last_event": {"read_only": True},
        }


class RequestSerializer(ModelSerializer):
    """Serializer for request"""

    class Meta:
        model = Request
        fields = [
            "id",
            "started_at",
            "duration",
            "method",
            "path",
            "route",
            "url_name",
            "app_name",
            "user",
        ]

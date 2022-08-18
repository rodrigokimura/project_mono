"""Watcher's serializers"""
from accounts.serializers import UserSerializer
from rest_framework.serializers import (
    BooleanField,
    CurrentUserDefault,
    ModelSerializer,
    Serializer,
)

from .models import Comment


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

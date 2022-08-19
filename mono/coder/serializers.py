"""Coder's serializers"""
from rest_framework import serializers

from .models import Configuration, Snippet, Tag

#  pylint: disable=cyclic-import
#  false positive pylint error


class ConfigurationSerializer(serializers.ModelSerializer):
    """Configuration serializer"""

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Configuration
        fields = [
            "id",
            "style",
            "linenos",
            "created_at",
            "updated_at",
            "created_by",
        ]


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer"""

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
            "color",
            "created_by",
        ]


class SnippetSerializer(serializers.ModelSerializer):
    """Snippet serializer"""

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Snippet
        fields = [
            "id",
            "title",
            "code",
            "language",
            "html",
            "public",
            "public_id",
            "created_by",
            "tags",
        ]
        read_only_fields = [
            "html",
            "public_id",
        ]

"""Coder's serializers"""
from rest_framework import serializers

from .models import Snippet, Tag


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer"""
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'color',
            'created_by',
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
            'id',
            'title',
            'code',
            'language',
            'html',
            'public',
            'public_id',
            'created_by',
            'tags',
        ]
        read_only_fields = [
            'html',
            'public_id',
        ]

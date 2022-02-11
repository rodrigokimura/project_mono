"""Coder's serializers"""
from rest_framework import serializers

from .models import Snippet


class SnippetSerializer(serializers.ModelSerializer):
    """Snippet serializer"""
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

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
        ]
        read_only_fields = [
            'html',
            'public_id',
        ]

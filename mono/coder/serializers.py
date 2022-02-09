"""Coder's serializers"""
from rest_framework import serializers

from .models import Snippet


class SnippetSerializer(serializers.ModelSerializer):
    """Snippet serializer"""
    class Meta:
        model = Snippet
        fields = [
            'id',
            'title',
            'code',
            'language',
            'html'
        ]
        read_only_fields = ['html']

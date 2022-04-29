"""Notes serializers"""
from rest_framework import serializers

from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    """Note serializer"""
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Note
        fields = [
            'title',
            'location',
            'text',
            'created_by',
        ]

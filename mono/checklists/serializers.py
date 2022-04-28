"""Todo lists's serializers"""
from rest_framework.serializers import (
    CurrentUserDefault, HiddenField, ModelSerializer,
)

from .models import Checklist, Task


class ChecklistSerializer(ModelSerializer):
    """
    Checklist serializer
    """
    created_by = HiddenField(
        default=CurrentUserDefault()
    )
    class Meta:
        model = Checklist
        fields = [
            'id',
            'name',
            'created_by',
        ]
        read_only_fields = ['created_by']


class TaskSerializer(ModelSerializer):
    """
    Task serializer
    """
    created_by = HiddenField(
        default=CurrentUserDefault()
    )
    class Meta:
        model = Task
        fields = [
            'id',
            'checklist',
            'description',
            'order',
            'created_by',
            'created_at',
            'checked_by',
            'checked_at',
        ]
        read_only_fields = ['created_by', 'checked_by', 'checked_at']

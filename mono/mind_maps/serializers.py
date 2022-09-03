"""Mind maps serializers"""
from rest_framework.serializers import (
    CurrentUserDefault,
    HiddenField,
    ModelSerializer,
)

from .models import MindMap, Node


class MindMapSerializer(ModelSerializer):
    """
    MindMap serializer
    """

    created_by = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = MindMap
        fields = [
            "id",
            "name",
            "created_by",
        ]
        read_only_fields = ["created_by"]


class NodeSerializer(ModelSerializer):
    """
    Node serializer
    """

    created_by = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Node
        fields = [
            "id",
            "name",
            "parent",
            "mind_map",
            "created_by",
            "created_at",
        ]
        read_only_fields = [
            "parent",
            "created_by",
            "created_at",
        ]

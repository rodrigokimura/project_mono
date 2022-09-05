"""Mind maps serializers"""
from rest_framework.serializers import (
    CurrentUserDefault,
    HiddenField,
    ModelSerializer,
)

from .models import MindMap, Node


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
            "position",
            "created_by",
            "created_at",
        ]
        read_only_fields = [
            "position",
            "parent",
            "created_by",
            "created_at",
        ]


class MindMapSerializer(ModelSerializer):
    """
    MindMap serializer
    """

    created_by = HiddenField(default=CurrentUserDefault())
    nodes = NodeSerializer(many=True, read_only=True)

    class Meta:
        model = MindMap
        fields = [
            "id",
            "name",
            "created_at",
            "created_by",
            "nodes",
        ]
        read_only_fields = [
            "created_at",
            "created_by",
        ]

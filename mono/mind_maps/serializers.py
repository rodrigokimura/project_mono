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
            "font_size",
            "padding",
            "border_size",
            "created_by",
            "created_at",
            "bold",
            "italic",
            "underline",
            "line_through",
            "font_color",
            "border_color",
            "background_color",
            "collapsed",
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
            "scale",
            "created_at",
            "created_by",
            "nodes",
        ]
        read_only_fields = [
            "created_at",
            "created_by",
        ]

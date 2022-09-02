"""Mind maps viewsets"""
from __mono.permissions import IsCreator
from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet

from .models import MindMap, Node
from .serializers import MindMapSerializer, NodeSerializer

# pylint: disable=too-many-ancestors


class MindMapViewSet(ModelViewSet):
    """Mind map viewset"""

    queryset = MindMap.objects.all()
    serializer_class = MindMapSerializer
    permission_classes = [IsCreator]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)


class NodeFilter(filters.FilterSet):
    """
    Node filter class
    """

    class Meta:
        model = Node
        fields = ["mind_map__id"]


class NodeViewSet(ModelViewSet):
    """Task viewset"""

    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    permission_classes = [IsCreator]
    filterset_class = NodeFilter

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)

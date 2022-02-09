"""Coder's viewsets"""
from __mono.permissions import IsCreator
from rest_framework.viewsets import ModelViewSet

from .models import Snippet
from .serializers import SnippetSerializer

# pylint: disable=R0901


class BaseViewSet(ModelViewSet):
    """Base viewset"""

    permission_classes = [IsCreator]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            created_by=self.request.user,
        )


class SnippetViewSet(BaseViewSet):
    """Snippet viewset"""
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

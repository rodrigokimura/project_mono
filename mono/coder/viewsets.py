"""Coder's viewsets"""
from time import sleep

from __mono.permissions import IsCreator
from django.db.models import Count, QuerySet
from rest_framework.decorators import action
from rest_framework.response import Response
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
    filterset_fields = ['language']


    @action(detail=False, methods=['get'])
    def languages(self, request):
        """Return list of languages"""
        snippets: QuerySet[Snippet] = self.get_queryset()
        return Response(
            snippets.values('language').annotate(
                count=Count('id', distinct=True),
            ).distinct()
        )

"""Coder's viewsets"""
from __mono.permissions import IsCreator
from django.db.models import Count, QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Snippet, Tag
from .serializers import SnippetSerializer, TagSerializer

# pylint: disable=R0901


class BaseViewSet(ModelViewSet):
    """Base viewset"""

    permission_classes = [IsCreator]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            created_by=self.request.user,
        )


class TagViewSet(BaseViewSet):
    """Tag viewset"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class SnippetViewSet(BaseViewSet):
    """Snippet viewset"""
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    filterset_fields = {
        'language': ['exact'],
        'tags__id': ['exact'],
        'tags': ['isnull'],
    }

    @action(detail=False, methods=['get'])
    def languages(self, request):
        """Return list of languages"""
        snippets: QuerySet[Snippet] = self.get_queryset()
        return Response(
            snippets.values('language').annotate(
                count=Count('id', distinct=True),
            ).distinct()
        )

    @action(detail=False, methods=['get'])
    def tags(self, request):
        """Return list of tags"""
        snippets: QuerySet[Snippet] = self.get_queryset()
        tags: QuerySet[Tag] = Tag.objects.filter(created_by=request.user)
        result = list(tags.annotate(
            count=Count('snippet__id'),
        ).values('id', 'name', 'color', 'count').distinct())
        result.append(
            {
                'id': None,
                'name': None,
                'count': snippets.filter(tags__isnull=True).count(),
            }
        )
        return Response(result)

    @action(detail=True, methods=['post'])
    def untag(self, request, *args, **kwargs):
        """Untag snippet"""
        snippet: Snippet = self.get_object()
        tag = get_object_or_404(Tag, id=request.data.get('tag'))
        snippet.tags.remove(tag)
        return Response(status=204)

    @action(detail=True, methods=['post'])
    def tag(self, request, *args, **kwargs):
        """Tag snippet"""
        snippet: Snippet = self.get_object()
        tag = get_object_or_404(Tag, id=request.data.get('tag'))
        snippet.tags.add(tag)
        return Response(status=204)

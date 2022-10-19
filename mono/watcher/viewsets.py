"""Watcher's viewsets"""
from __mono.permissions import IsCreator
from django.db.models import Count, DateTimeField, Max, Min, Sum
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from .models import Comment, Issue
from .serializers import CommentSerializer, IssueSerializer

# pylint: disable=too-many-ancestors


class CommentViewSet(ModelViewSet):
    """Comment viewset"""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsCreator, IsAdminUser]
    filterset_fields = {
        "issue__id": ["exact"],
    }


class IssueViewSet(ModelViewSet):
    """Issue viewset"""

    queryset = Issue.objects.annotate(
        events=Count("event"),
        users=Count("event__user", distinct=True),
        first_event=Min("event__timestamp", output_field=DateTimeField()),
        last_event=Max("event__timestamp", output_field=DateTimeField()),
    )
    serializer_class = IssueSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = {
        "resolved_at": ["isnull"],
    }

"""Watcher's viewsets"""
from __mono.permissions import IsCreator
from django.db.models import Avg, Count, DateTimeField, Max, Min
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Comment, Issue, Request
from .serializers import CommentSerializer, IssueSerializer, RequestSerializer

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


class RequestViewSet(ModelViewSet):
    """Request viewset"""

    queryset = Request.objects.all().order_by("id")
    serializer_class = RequestSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = {
        "app_name": ["exact"],
    }

    @action(detail=False, methods=["get"])
    def app_name(self, *args, **kwargs):
        """Avg duration of requests by app_name"""
        return Response(
            self.queryset.values("app_name")
            .annotate(
                avg_duration=Avg("duration"),
                total_count=Count("id"),
            )
            .order_by()
        )

"""Checklists viewsets"""
from __mono.permissions import IsCreator
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Checklist, Task
from .serializers import ChecklistSerializer, TaskSerializer

# pylint: disable=too-many-ancestors


class ChecklistViewSet(ModelViewSet):
    """Checklist viewset"""

    queryset = Checklist.objects.order_by('id').all()
    serializer_class = ChecklistSerializer
    permission_classes = [IsCreator]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)


class TaskViewSet(ModelViewSet):
    """Task viewset"""

    queryset = Task.objects.order_by('id').all()
    serializer_class = TaskSerializer
    permission_classes = [IsCreator]
    filterset_fields = {
        'checklist__id': ['exact'],
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def check(self, request, *args, **kwargs):
        """Mark task as checked"""
        task: Task = self.get_object()
        task.mark_as_checked(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def uncheck(self, request, *args, **kwargs):
        """Mark task as unchecked"""
        task: Task = self.get_object()
        task.mark_as_unchecked()
        return Response(status=status.HTTP_204_NO_CONTENT)

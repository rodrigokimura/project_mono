"""Checklists viewsets"""
from __mono.permissions import IsCreator
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Checklist, Task
from .serializers import ChecklistSerializer, TaskSerializer

# pylint: disable=too-many-ancestors


class ChecklistViewSet(ModelViewSet):
    """Checklist viewset"""

    queryset = Checklist.objects.all()
    serializer_class = ChecklistSerializer
    permission_classes = [IsCreator]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def sort(self, request, *args, **kwargs):
        """Sort checklist tasks"""
        checklist: Checklist = self.get_object()
        tasks = Task.objects.filter(checklist=checklist)
        if request.data.get('field') not in ['description', 'created_at']:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        is_ascending = request.data.get('direction', 'asc').lower() == 'asc'

        tasks = tasks.order_by(
            request.data['field']
            if is_ascending else '-' + request.data['field']
        )
        for index, task in enumerate(tasks):
            task.order = index
            task.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskViewSet(ModelViewSet):
    """Task viewset"""

    queryset = Task.objects.all()
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

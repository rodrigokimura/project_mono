"""Finance's viewsets"""
from __mono.permissions import IsCreator
from rest_framework.viewsets import ModelViewSet

from .models import Checklist, Task, User
from .serializers import ChecklistSerializer, TaskSerializer

# pylint: disable=R0901


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

"""Typer viewsets"""
from __mono.permissions import IsCreator
from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet

from .models import Lesson, Record
from .serializers import LessonSerializer, RecordSerializer

# pylint: disable=too-many-ancestors


class LessonViewSet(ModelViewSet):
    """Lesson viewset"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsCreator]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)


class RecordFilter(filters.FilterSet):
    """
    Record filter class
    """

    class Meta:
        model = Record
        fields = ["lesson__id"]


class RecordViewSet(ModelViewSet):
    """Record viewset"""

    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    permission_classes = [IsCreator]
    filterset_class = RecordFilter

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)

"""Checklists' views"""
from __mono.permissions import IsCreator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Configuration
from .serializers import (
    ChecklistMoveSerializer, ConfigurationSerializer, TaskMoveSerializer,
)


class HomePageView(LoginRequiredMixin, TemplateView):
    """
    Root view
    """

    template_name = "checklists/home.html"


class ChecklistMoveApiView(LoginRequiredMixin, APIView):
    """
    Change checklist order.
    """

    def post(self, request):
        """
        Apply checklist movement.
        """
        serializer = ChecklistMoveSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskMoveApiView(LoginRequiredMixin, APIView):
    """
    Change task order in a checklist.
    """

    def post(self, request):
        """
        Apply task movement.
        """
        serializer = TaskMoveSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfigAPIView(RetrieveUpdateAPIView):
    """View to read or update user config"""

    serializer_class = ConfigurationSerializer
    permission_classes = [IsCreator]

    def get_object(self):
        return Configuration.objects.get_or_create(created_by=self.request.user)[0]

"""Todo Lists' views"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ChecklistMoveSerializer, TaskMoveSerializer


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
            return Response(serializer.data)
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
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

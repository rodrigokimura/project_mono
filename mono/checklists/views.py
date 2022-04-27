"""Todo Lists' views"""
from __mono.mixins import PassRequestToFormViewMixin
from __mono.views import ProtectedDeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls.base import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import ListForm
from .models import Checklist, Task
from .serializers import ChecklistSerializer, TaskSerializer


class HomePageView(LoginRequiredMixin, TemplateView):
    """
    Root view
    """

    template_name = "checklists/home.html"

    def get(self, request, *args, **kwargs):
        """
        Redirect to todo list creation
        when user has no todo lists yet
        """
        if not request.user.checklists.all().exists():
            return redirect('checklists:list_create')
        return super().get(request, *args, **kwargs)


class ListCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    """
    Create new todo list
    """
    model = Checklist
    form_class = ListForm
    success_url = reverse_lazy('checklists:index')
    success_message = "%(name)s was created successfully"

    def get_success_url(self):
        """
        Add todo list to session
        """
        self.request.session['checklists'] = self.object.pk
        return super().get_success_url()


class ListUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    """
    Update todo list
    """
    model = Checklist
    form_class = ListForm
    success_url = reverse_lazy('checklists:index')
    success_message = "%(name)s was updated successfully"


class ListDeleteView(ProtectedDeleteView):
    """
    Delete todo list
    """
    model = Checklist
    success_url = reverse_lazy('checklists:index')
    success_message = "List was deleted successfully"

# API views

class TaskCheckApiView(APIView):
    """
    Mark task as checked
    """

    def post(self, request, pk, **kwargs):
        """
        Mark task as checked
        """
        task = get_object_or_404(Task, pk=pk)
        task.mark_as_checked(request.user)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskUncheckApiView(APIView):
    """
    Mark task as unchecked
    """

    def post(self, request, pk, **kwargs):
        """
        Mark task as unchecked
        """
        task = get_object_or_404(Task, pk=pk)
        task.mark_as_unchecked()
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

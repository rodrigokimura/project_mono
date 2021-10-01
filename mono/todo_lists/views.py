from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls.base import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import ListForm
from .mixins import PassRequestToFormViewMixin
from .models import List, Task
from .serializers import ListSerializer, TaskSerializer


class HomePageView(LoginRequiredMixin, TemplateView):

    template_name = "todo_lists/home.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.list_set.all().count() == 0:
            return redirect('todo_lists:list_create')
        return super().dispatch(request, *args, **kwargs)


class ListCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = List
    form_class = ListForm
    success_url = reverse_lazy('todo_lists:index')
    success_message = "%(name)s was created successfully"


class ListUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = List
    form_class = ListForm
    success_url = reverse_lazy('todo_lists:index')
    success_message = "%(name)s was updated successfully"


class ListDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = List
    success_url = reverse_lazy('todo_lists:index')
    success_message = "List was deleted successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# API views

class ListListAPIView(APIView):
    """
    List all lists, or create a new list.
    """

    def get(self, request, format=None):
        lists = List.objects.filter(created_by=request.user)
        serializer = ListSerializer(lists, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListDetailAPIView(APIView):
    """
    Retrieve, update or delete a list instance.
    """

    def get_object(self, pk):
        try:
            return List.objects.get(pk=pk)
        except List.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        list = self.get_object(pk)
        serializer = ListSerializer(list)
        request.session['todo_list'] = pk
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        list = self.get_object(pk)
        serializer = ListSerializer(list, data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        list = self.get_object(pk)
        list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskListAPIView(APIView):
    """
    List all tasks, or create a new task.
    """

    def get(self, request, format=None, **kwargs):
        tasks = Task.objects.filter(list=kwargs['list_pk'])
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            if 'list_pk' in kwargs.keys():
                list = get_object_or_404(List, pk=kwargs['list_pk'])
                if list.created_by == request.user:
                    serializer.save(created_by=request.user, list=list)
                else:
                    raise PermissionDenied
            else:
                serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailAPIView(APIView):
    """
    Retrieve, update or delete a task instance.
    """

    def get_object(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None, **kwargs):
        task = self.get_object(pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk, format=None, **kwargs):
        task = self.get_object(pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None, **kwargs):
        task = self.get_object(pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None, **kwargs):
        task = self.get_object(pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskCheckApiView(APIView):
    """
    Mark task as checked
    """

    def get_object(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise Http404

    def post(self, request, pk, **kwargs):
        task = self.get_object(pk)
        task.mark_as_checked(request.user)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskUncheckApiView(APIView):
    """
    Mark task as unchecked
    """

    def get_object(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise Http404

    def post(self, request, pk, **kwargs):
        task = self.get_object(pk)
        task.mark_as_unchecked(request.user)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

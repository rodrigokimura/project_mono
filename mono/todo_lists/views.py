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
from .models import List, Task
from .serializers import ListSerializer, TaskSerializer


class HomePageView(LoginRequiredMixin, TemplateView):
    """
    Root view
    """

    template_name = "todo_lists/home.html"

    def get(self, request, *args, **kwargs):
        """
        Redirect to todo list creation
        when user has no todo lists yet
        """
        if request.user.todo_lists.all().count() == 0:
            return redirect('todo_lists:list_create')
        return super().get(request, *args, **kwargs)


class ListCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    """
    Create new todo list
    """
    model = List
    form_class = ListForm
    success_url = reverse_lazy('todo_lists:index')
    success_message = "%(name)s was created successfully"

    def get_success_url(self):
        """
        Add todo list to session
        """
        self.request.session['todo_list'] = self.object.pk
        return super().get_success_url()


class ListUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    """
    Update todo list
    """
    model = List
    form_class = ListForm
    success_url = reverse_lazy('todo_lists:index')
    success_message = "%(name)s was updated successfully"


class ListDeleteView(ProtectedDeleteView):
    """
    Delete todo list
    """
    model = List
    success_url = reverse_lazy('todo_lists:index')
    success_message = "List was deleted successfully"

# API views


class ListListAPIView(APIView):
    """
    List all lists, or create a new list.
    """

    def get(self, request):
        """
        List all user's todo lists
        """
        todo_lists = List.objects.filter(created_by=request.user)
        serializer = ListSerializer(todo_lists, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new todo list
        """
        serializer = ListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListDetailAPIView(APIView):
    """
    Retrieve, update or delete a list instance.
    """

    def get(self, request, pk):
        """
        Retrieve todo list
        """
        todo_list = get_object_or_404(List, pk=pk)
        serializer = ListSerializer(todo_list)
        request.session['todo_list'] = pk
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Edit todo list
        """
        todo_list = get_object_or_404(List, pk=pk)
        serializer = ListSerializer(todo_list, data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete todo list
        """
        todo_list = get_object_or_404(List, pk=pk)
        todo_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskListAPIView(APIView):
    """
    List all tasks, or create a new task.
    """

    def get(self, request, **kwargs):
        """
        List all tasks in a todo list
        """
        tasks = Task.objects.filter(list=kwargs['list_pk'])
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, **kwargs):
        """
        Create new task
        """
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if 'list_pk' in kwargs:
            todo_list = get_object_or_404(List, pk=kwargs['list_pk'])
            if todo_list.created_by != request.user:
                raise PermissionDenied
            serializer.save(created_by=request.user, list=todo_list)
        else:
            serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskDetailAPIView(APIView):
    """
    Retrieve, update or delete a task instance.
    """

    def get(self, request, pk, **kwargs):
        """
        Retrieve task
        """
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk, **kwargs):
        """
        Edit task
        """
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, **kwargs):
        """
        Edit task
        """
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, **kwargs):
        """
        Delete task
        """
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

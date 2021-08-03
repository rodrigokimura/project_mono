from django.core.exceptions import BadRequest
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls.base import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Board, Bucket, Card
from .forms import ProjectForm, BoardForm
from .mixins import PassRequestToFormViewMixin
from .serializers import BucketMoveSerializer, CardMoveSerializer, ProjectSerializer, BoardSerializer, BucketSerializer, CardSerializer


class ProjectListView(ListView):
    model = Project
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Projects', None),
        ]
        return context


class ProjectDetailView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Project: view', None),
        ]
        return context


class ProjectCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('project_manager:projects')
    success_message = "%(name)s was created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Project: create', None),
        ]
        return context


class ProjectUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('project_manager:projects')
    success_message = "%(name)s was updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Project: edit', None),
        ]
        return context


class ProjectDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Project
    success_url = reverse_lazy('project_manager:projects')
    success_message = "Project was deleted successfully"

    def test_func(self):
        return self.get_object().owned_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ProjectDeleteView, self).delete(request, *args, **kwargs)


class BoardListView(ListView):
    model = Board
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Boards', None),
        ]
        return context


class BoardDetailView(DetailView):
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            (f'Project: {self.object}', reverse('project_manager:project_detail', args=[self.object.id])),
            ('Board: view', None),
        ]
        return context


class BoardCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Board
    form_class = BoardForm
    success_url = reverse_lazy('project_manager:boards')
    success_message = "%(name)s was created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Board: create', None),
        ]
        return context


class BoardUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = Board
    form_class = BoardForm
    success_url = reverse_lazy('project_manager:boards')
    success_message = "%(name)s was updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Board: edit', None),
        ]
        return context


class BoardDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Board
    success_url = reverse_lazy('project_manager:boards')
    success_message = "Board was deleted successfully"

    def test_func(self):
        return self.get_object().owned_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ProjectDeleteView, self).delete(request, *args, **kwargs)


# API Views

class ProjectListAPIView(APIView):
    """
    List all snippets, or create a new snippet.
    """

    def get(self, request, format=None):
        snippets = Project.objects.all()
        serializer = ProjectSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailAPIView(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = ProjectSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = ProjectSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoardListAPIView(APIView):
    """
    List all snippets, or create a new snippet.
    """

    def get(self, request, format=None):
        snippets = Board.objects.all()
        serializer = BoardSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = BoardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardDetailAPIView(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_object(self, pk):
        try:
            return Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = BoardSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = BoardSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BucketListAPIView(APIView):
    """
    List all snippets, or create a new snippet.
    """

    def get(self, request, format=None, **kwargs):
        buckets = Bucket.objects.all()
        serializer = BucketSerializer(buckets, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        serializer = BucketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                created_by=request.user,
                order=board.max_order + 1,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BucketDetailAPIView(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_object(self, pk):
        try:
            return Bucket.objects.get(pk=pk)
        except Bucket.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        bucket = self.get_object(pk)
        serializer = BucketSerializer(bucket)
        return Response(serializer.data)

    def put(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        bucket = self.get_object(pk)

        if request.user in board.allowed_users:
            serializer = BucketSerializer(bucket, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return BadRequest

    def delete(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        if request.user in board.allowed_users:
            bucket = self.get_object(pk)
            bucket.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return BadRequest


class CardListAPIView(APIView):
    """
    List all snippets, or create a new snippet.
    """

    def get(self, request, format=None, **kwargs):
        project_pk = kwargs.get('project_pk')
        board_pk = kwargs.get('board_pk')
        bucket_pk = kwargs.get('bucket_pk')
        project = Project.objects.get(id=project_pk)
        board = Board.objects.get(project=project, id=board_pk)
        bucket = Bucket.objects.get(board=board, id=bucket_pk)
        cards = Card.objects.filter(bucket=bucket)
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        if request.user in board.allowed_users:
            serializer = CardSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    created_by=request.user,
                    order=bucket.max_order + 1,
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return BadRequest


class CardDetailAPIView(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_object(self, pk):
        try:
            return Card.objects.get(pk=pk)
        except Card.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = CardSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        card = self.get_object(pk)
        if request.user in card.allowed_users:
            serializer = CardSerializer(card, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise BadRequest

    def delete(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        card = self.get_object(pk)
        if request.user in card.allowed_users:
            card.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise BadRequest


class CardMoveApiView(APIView):
    """
    Move card from one bucket to another bucket in given order.
    """

    def post(self, request, format=None):
        serializer = CardMoveSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BucketMoveApiView(APIView):
    """
    Change bucket order in a board.
    """

    def post(self, request, format=None):
        serializer = BucketMoveSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StartStopTimerAPIView(APIView):
    """
    Start or stop timer of a given card.
    """

    def get_object(self, pk):
        try:
            return Card.objects.get(pk=pk)
        except Card.DoesNotExist:
            raise Http404

    def post(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        card = self.get_object(pk)
        if request.user in card.allowed_users:
            result = card.start_stop_timer(user=request.user)
            return Response({
                'success': True,
                'action': result['action']
            })
        else:
            raise BadRequest

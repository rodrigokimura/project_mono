from typing import Optional
from django.conf import settings
from django.core.exceptions import BadRequest
from django.db.models.query import QuerySet
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import HttpResponse
from django.urls.base import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from .models import Project, Board, Bucket, Card, Theme, Invite
from .forms import ProjectForm, BoardForm
from .mixins import PassRequestToFormViewMixin
from .serializers import BucketMoveSerializer, CardMoveSerializer, InviteSerializer, ProjectSerializer, BoardSerializer, BucketSerializer, CardSerializer


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    paginate_by = 100

    def get_queryset(self) -> QuerySet[Project]:
        qs = super().get_queryset()
        created_projects = qs.filter(created_by=self.request.user)
        assigned_projects = qs.filter(assigned_to=self.request.user)
        return (created_projects | assigned_projects).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
        ]
        return context


class ProjectDetailView(UserPassesTestMixin, DetailView):
    model = Project

    def test_func(self) -> Optional[bool]:
        project = self.get_object()
        return self.request.user in project.allowed_users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            (self.object.name, None),
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
            ('Create project', None),
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
            ('Edit project', None),
        ]
        return context


class BoardDetailView(LoginRequiredMixin, DetailView):
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            (self.object.project.name, reverse('project_manager:project_detail', args=[self.object.project.id])),
            (self.object.name, None),
        ]
        context['card_statuses'] = Card.STATUSES
        context['bucket_auto_statuses'] = Bucket.STATUSES
        context['colors'] = Theme.objects.all()
        return context


class BoardCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Board
    form_class = BoardForm
    success_url = reverse_lazy('project_manager:boards')
    success_message = "%(name)s was created successfully"

    def get_success_url(self, **kwargs) -> str:
        success_url = reverse_lazy('project_manager:project_detail', args=[str(self.request.POST.get('project'))])
        return success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project_pk'] = self.kwargs['project_pk']
        return kwargs

    def get_context_data(self, **kwargs):
        project = Project.objects.get(id=self.kwargs['project_pk'])
        context = super().get_context_data(**kwargs)
        context['project'] = project
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            (project.name, reverse('project_manager:project_detail', args=[project.id])),
            ('Create board', None),
        ]
        return context


class BoardUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = Board
    form_class = BoardForm
    success_url = reverse_lazy('project_manager:boards')
    success_message = "%(name)s was updated successfully"

    def get_success_url(self, **kwargs) -> str:
        success_url = reverse_lazy('project_manager:project_detail', args=[str(self.request.POST.get('project'))])
        return success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project_pk'] = self.kwargs['project_pk']
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Board: edit', None),
        ]
        return context


class InviteAcceptanceView(LoginRequiredMixin, TemplateView):
    template_name = "project_manager/invite_acceptance.html"

    def get(self, request):
        token = request.GET.get('t', None)

        if token is None:
            return HttpResponse("error")
        else:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )

            invite = get_object_or_404(Invite, pk=payload['id'])
            user_already_member = request.user in invite.project.assigned_to.all()
            if not invite.accepted and not user_already_member:
                invite.accept(request.user)
                invite.save()
            return self.render_to_response({
                "accepted": invite.accepted,
                "user_already_member": user_already_member,
            })

# API Views


class ProjectListAPIView(LoginRequiredMixin, APIView):
    """
    List all snippets, or create a new snippet.
    """

    def get(self, request, format=None):
        projects = Project.objects.filter(created_by=request.user)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        project = self.get_object(pk)
        if request.user in project.allowed_users:
            serializer = ProjectSerializer(project, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return BadRequest

    def delete(self, request, pk, format=None, **kwargs):
        project = self.get_object(pk)
        if request.user in project.allowed_users:
            project.delete()
            return Response({
                'success': True,
                'url': reverse_lazy('project_manager:projects')
            })
        return BadRequest


class BoardListAPIView(LoginRequiredMixin, APIView):
    """
    List all snippets, or create a new snippet.
    """

    def get(self, request, format=None):
        boards = Board.objects.filter(created_by=request.user)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        serializer = BoardSerializer(data=request.data)
        if request.user in project.allowed_users:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return BadRequest


class BoardDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a board instance.
    """

    def get_object(self, pk):
        try:
            return Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        board = self.get_object(pk)
        serializer = BoardSerializer(board)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        board = self.get_object(pk)
        serializer = BoardSerializer(board, data=request.data)
        if request.user in board.allowed_users:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return BadRequest

    def delete(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = self.get_object(pk)
        if request.user in board.allowed_users:
            board.delete()
            return Response({
                'success': True,
                'url': reverse_lazy('project_manager:project_detail', args=[project.id])
            })
        return BadRequest


class BucketListAPIView(LoginRequiredMixin, APIView):
    """
    List all buckets, or create a new bucket.
    """

    def get(self, request, format=None, **kwargs):
        board = Board.objects.get(id=kwargs['board_pk'])
        buckets = Bucket.objects.filter(board=board)
        if request.user in board.allowed_users:
            serializer = BucketSerializer(buckets, many=True, context={'request': request})
            return Response(serializer.data)
        return BadRequest

    def post(self, request, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        serializer = BucketSerializer(data=request.data)
        if request.user in board.allowed_users:
            if serializer.is_valid():
                theme_id = request.data.get('color')
                if theme_id != '':
                    color = Theme.objects.get(id=theme_id)
                    serializer.save(
                        created_by=request.user,
                        order=board.max_order + 1,
                        color=color,
                    )
                else:
                    serializer.save(
                        created_by=request.user,
                        order=board.max_order + 1,
                        color=None,
                    )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return BadRequest


class BucketDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a bucket instance.
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
                theme_id = request.data.get('color')
                if theme_id != '':
                    color = Theme.objects.get(id=theme_id)
                    bucket.color = color
                    bucket.save()
                else:
                    bucket.color = None
                    bucket.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return BadRequest

    def delete(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        if request.user in board.allowed_users:
            bucket = self.get_object(pk)
            bucket.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return BadRequest


class CardListAPIView(LoginRequiredMixin, APIView):
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
            serializer = CardSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                theme_id = request.data.get('color')
                if theme_id != '':
                    color = Theme.objects.get(id=theme_id)
                    serializer.save(
                        created_by=request.user,
                        order=bucket.max_order + 1,
                        color=color
                    )
                else:
                    serializer.save(
                        created_by=request.user,
                        order=bucket.max_order + 1,
                    )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return BadRequest


class CardDetailAPIView(LoginRequiredMixin, APIView):
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
            serializer = CardSerializer(card, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                theme_id = request.data.get('color')
                if theme_id != '':
                    color = Theme.objects.get(id=theme_id)
                    card.color = color
                    card.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        raise BadRequest

    def delete(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        card = self.get_object(pk)
        if request.user in card.allowed_users:
            card.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise BadRequest


class CardMoveApiView(LoginRequiredMixin, APIView):
    """
    Move card from one bucket to another bucket in given order.
    """

    def post(self, request, format=None):
        serializer = CardMoveSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.move()
            return Response(result)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BucketMoveApiView(LoginRequiredMixin, APIView):
    """
    Change bucket order in a board.
    """

    def post(self, request, format=None):
        serializer = BucketMoveSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StartStopTimerAPIView(LoginRequiredMixin, APIView):
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
        raise BadRequest


class InviteListAPIView(LoginRequiredMixin, APIView):
    """
    List all invites, or create a new invite.
    """

    def get(self, request, format=None, **kwargs):
        project_pk = kwargs.get('project_pk')
        project = Project.objects.get(id=project_pk)
        if request.user in project.allowed_users:
            invites = Invite.objects.filter(
                project=project,
                email__isnull=False,
            ).exclude(email__exact='')
            serializer = InviteSerializer(invites, many=True)
            return Response(serializer.data)
        return BadRequest

    def post(self, request, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        serializer = InviteSerializer(data=request.data, context={'request': request})
        if request.user in project.allowed_users:
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return BadRequest


class InviteDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a invite instance.
    """

    def get_object(self, pk):
        try:
            return Invite.objects.get(pk=pk)
        except Invite.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        if request.user in project.allowed_users:
            invite = self.get_object(pk)
            serializer = InviteSerializer(invite)
            return Response(serializer.data)
        return BadRequest

    def put(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        invite = self.get_object(pk)
        if request.user in project.allowed_users:
            serializer = InviteSerializer(invite, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        raise BadRequest

    def delete(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        invite = self.get_object(pk)
        if request.user in project.allowed_users:
            invite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise BadRequest

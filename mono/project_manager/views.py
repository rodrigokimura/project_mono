"""Project manager's views."""
from typing import Any, Optional

from __mono.mixins import PassRequestToFormViewMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.humanize.templatetags.humanize import NaturalTimeFormatter
from django.contrib.messages.views import SuccessMessageMixin
from django.core.signing import TimestampSigner
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls.base import reverse, reverse_lazy
from django.utils import dateparse
from django.utils.translation import gettext as _
from django.views.generic import ListView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import BoardForm, ProjectForm
from .models import (
    Board, Bucket, Card, CardFile, Comment, Icon, Invite, Item, Project, Tag,
    Theme, TimeEntry, User,
)
from .serializers import (
    BoardMoveSerializer, BoardSerializer, BucketMoveSerializer,
    BucketSerializer, CardFileSerializer, CardMoveSerializer, CardSerializer,
    CommentSerializer, InviteSerializer, ItemSerializer, ProjectSerializer,
    TagSerializer, TimeEntrySerializer,
)


class ProjectListView(LoginRequiredMixin, ListView):
    """
    List all user's projects.
    """
    model = Project
    paginate_by = 100

    def get_queryset(self) -> QuerySet[Project]:
        """
        Set queryset to only include projects the user is a member of.
        """
        qs = super().get_queryset()

        field = self.request.GET.get('field')
        direction = self.request.GET.get('direction', 'asc')
        if field:
            if direction == 'asc':
                qs = qs.order_by(field)
            else:
                qs = qs.order_by(f'-{field}')

        created_projects = qs.filter(created_by=self.request.user)
        assigned_projects = qs.filter(assigned_to=self.request.user)

        return (created_projects | assigned_projects).distinct()

    def get_context_data(self, **kwargs):
        """
        Set context data to template.
        """
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            (_('Home'), reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
        ]
        return context


class ProjectDetailView(UserPassesTestMixin, DetailView):
    """
    List all boards in a project.
    """
    model = Project

    def test_func(self) -> Optional[bool]:
        project = self.get_object()
        return self.request.user in project.allowed_users

    def get_context_data(self, **kwargs):
        """
        Set context data to template and queryset filters.
        """
        context = super().get_context_data(**kwargs)

        qs: QuerySet[Board] = self.get_object().board_set.all().order_by('order')

        field = self.request.GET.get('field')
        direction = self.request.GET.get('direction', 'asc')
        if field:
            if direction == 'asc':
                qs = qs.order_by(field)
            else:
                qs = qs.order_by(f'-{field}')

        context['boards'] = qs

        context['breadcrumb'] = [
            (_('Home'), reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            (self.object.name, None),
        ]
        return context


class ProjectCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    """
    Create a new project.
    """
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('project_manager:projects')
    success_message = "Project %(name)s was created successfully"

    def get_context_data(self, **kwargs):
        """
        Set context data to template.
        """
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            (_('Home'), reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Create project', None),
        ]
        return context

    def get_success_url(self):
        """
        Redirect to project detail view after its creation.
        """
        return reverse_lazy('project_manager:project_detail', kwargs={'pk': self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    """
    Update a given project.
    """
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('project_manager:projects')
    success_message = "Project %(name)s was updated successfully"

    def get_context_data(self, **kwargs):
        """
        Set context data to template.
        """
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            (_('Home'), reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Edit project', None),
        ]
        return context


class BoardDetailView(LoginRequiredMixin, DetailView):
    """
    Show all items in a board.
    """
    model = Board

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Handle permission checks.
        """
        board = self.get_object()
        if request.user in board.allowed_users:
            return super().get(request, *args, **kwargs)
        messages.error(request, 'You are not assigned to this board!')
        return redirect(to=reverse('project_manager:project_detail', args=[board.project.id]))

    def get_context_data(self, **kwargs):
        """
        Set context data to template.
        """
        context = super().get_context_data(**kwargs)
        card_statuses = []
        for value, name in Card.STATUSES:
            if value == Bucket.NOT_STARTED:
                card_statuses.append(
                    ('circle outline', value, name)
                )
            elif value == Bucket.IN_PROGRESS:
                card_statuses.append(
                    ('dot circle outline', value, name)
                )
            elif value == Bucket.COMPLETED:
                card_statuses.append(
                    ('check circle outline', value, name)
                )
        context['card_statuses'] = card_statuses
        context['bucket_auto_statuses'] = Bucket.STATUSES
        context['colors'] = Theme.objects.all()
        context['icons'] = Icon.objects.all()
        return context


class BoardCalendarView(LoginRequiredMixin, DetailView):
    """
    Show items in a board in a calendar view.
    """
    model = Board
    template_name = "project_manager/board_calendar.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Handle permission checks.
        """
        board = self.get_object()
        if request.user in board.allowed_users:
            return super().get(request, *args, **kwargs)
        messages.error(request, _('You are not assigned to this board!'))
        return redirect(to=reverse('project_manager:project_detail', args=[board.project.id]))

    def get_context_data(self, **kwargs):
        """
        Set context data to template.
        """
        context = super().get_context_data(**kwargs)
        card_statuses = []
        for value, name in Card.STATUSES:
            if value == Bucket.NOT_STARTED:
                card_statuses.append(
                    ('circle outline', value, name)
                )
            elif value == Bucket.IN_PROGRESS:
                card_statuses.append(
                    ('dot circle outline', value, name)
                )
            elif value == Bucket.COMPLETED:
                card_statuses.append(
                    ('check circle outline', value, name)
                )
        context['card_statuses'] = card_statuses
        context['bucket_auto_statuses'] = Bucket.STATUSES
        context['colors'] = Theme.objects.all()
        context['icons'] = Icon.objects.all()
        return context


class BoardCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    """
    Create a new board.
    """
    model = Board
    form_class = BoardForm
    success_url = reverse_lazy('project_manager:boards')
    success_message = _("Board %(name)s was created successfully")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Handle permission checks.
        """
        project = Project.objects.get(id=self.kwargs['project_pk'])
        if request.user == project.created_by:
            return super().get(request, *args, **kwargs)
        messages.error(request, _("You don't have permission to create boards in this project."))
        return redirect(to=reverse('project_manager:project_detail', args=[project.id]))

    def get_success_url(self) -> str:
        """
        Redirect to board detail view after its creation.
        """
        return reverse_lazy(
            'project_manager:board_detail',
            kwargs={
                'project_pk': self.object.project.pk,
                'pk': self.object.pk,
            }
        )

    def get_form_kwargs(self):
        """
        Add item to form kwargs.
        """
        kwargs = super().get_form_kwargs()
        kwargs['project_pk'] = self.kwargs['project_pk']
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Set context data to template.
        """
        project = Project.objects.get(id=self.kwargs['project_pk'])
        context = super().get_context_data(**kwargs)
        context['project'] = project
        context['breadcrumb'] = [
            (_('Home'), reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            (project.name, reverse('project_manager:project_detail', args=[project.id])),
            (_('Create board'), None),
        ]
        return context


class BoardUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    """
    Update a given board.
    """
    model = Board
    form_class = BoardForm
    success_url = reverse_lazy('project_manager:boards')
    success_message = _("Board %(name)s was updated successfully")

    def get_success_url(self) -> str:
        """
        Redirect to project detail view after board update.
        """
        return reverse_lazy('project_manager:project_detail', kwargs={'pk': self.object.project.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project_pk'] = self.kwargs['project_pk']
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            (_('Home'), reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            (_('Board: edit'), None),
        ]
        return context


class InviteAcceptanceView(LoginRequiredMixin, RedirectView):
    """
    Accept invitation to a board.
    """
    template_name = "project_manager/invite_acceptance.html"

    def get_redirect_url(self, *args, **kwargs) -> Optional[str]:
        """
        Redirect URL after invite acceptance.
        """
        super().get_redirect_url(*args, **kwargs)
        token = self.request.GET.get('t', None)
        if token is None:
            messages.add_message(self.request, messages.ERROR, _('No token provided.'))
            return reverse('home')
        signer = TimestampSigner(salt="project_invite")
        invite_id = signer.unsign_object(
            token,
            max_age=24 * 60 * 60 * 60
        )['id']
        invite = get_object_or_404(Invite, pk=invite_id)
        if invite.accepted:
            messages.add_message(self.request, messages.SUCCESS, _("You've already accepted this invitation."))
            return reverse('home')
        user_already_member = self.request.user in invite.project.assigned_to.all()
        if user_already_member:
            messages.add_message(self.request, messages.ERROR, _('You are already a member of this project.'))
            return reverse('home')

        invite.accept(self.request.user)
        invite.save()
        messages.add_message(self.request, messages.SUCCESS, _('Invite accepted.'))
        return reverse('project_manager:project_detail', args=[invite.project.id])


# API Views


class ProjectListAPIView(LoginRequiredMixin, APIView):
    """
    List all projects, or create a new project.
    """

    def get(self, request):
        """
        List all projects.
        """
        projects = Project.objects.filter(created_by=request.user)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new project
        """
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a project instance.
    """

    def get(self, request, pk):
        """
        Retrieve a project.
        """
        project: Project = get_object_or_404(Project, pk=pk)
        if request.user not in project.allowed_users:
            return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Edit project
        """
        project: Project = get_object_or_404(Project, pk=pk)
        if request.user not in project.allowed_users:
            return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete project
        """
        project: Project = get_object_or_404(Project, pk=pk)
        if request.user not in project.allowed_users:
            return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)
        project.delete()
        return Response({
            'success': True,
            'url': reverse_lazy('project_manager:projects')
        })


class ProjectRemoveUserAPIView(LoginRequiredMixin, APIView):
    """
    Remove user from project's team.
    """

    def post(self, request, project_pk):
        """
        Apply user removal from a project's team.
        """
        project: Project = get_object_or_404(Project, pk=project_pk)
        if request.user not in project.allowed_users:
            return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)
        user: User = get_object_or_404(User, pk=int(request.data.get('user')))
        if user not in project.assigned_to.all():
            return Response('User not a member of this project', status=status.HTTP_400_BAD_REQUEST)
        project.assigned_to.remove(user)
        Invite.objects.filter(project=project, accepted_by=user).delete()
        return Response({
            'success': True,
            'url': reverse_lazy('project_manager:projects')
        }, status=status.HTTP_200_OK)


class BoardListAPIView(LoginRequiredMixin, APIView):
    """
    List all projects, or create a new project.
    """

    def get(self, request, **kwargs):
        """
        List all boards in a project.
        """
        boards = Board.objects.filter(created_by=request.user)
        project = Project.objects.get(id=kwargs.get('project_pk'))
        if request.user not in project.allowed_users:
            return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    def post(self, request, **kwargs):
        """
        Create a new board.
        """
        project = Project.objects.get(id=kwargs.get('project_pk'))
        if request.user not in project.allowed_users:
            return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)
        serializer = BoardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a board instance.
    """

    def get(self, request, pk, **kwargs):
        """
        Retrieve board
        """
        board: Board = get_object_or_404(Board, pk=pk)
        if request.user not in board.allowed_users:
            return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)
        serializer = BoardSerializer(board)
        return Response(serializer.data)

    def put(self, request, pk, **kwargs):
        """
        Edit board
        """
        board: Board = get_object_or_404(Board, pk=pk)
        serializer = BoardSerializer(board, data=request.data)
        if request.user in board.allowed_users:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk, **kwargs):
        """
        Edit board
        """
        board: Board = get_object_or_404(Board, pk=pk)
        serializer = BoardSerializer(board, data=request.data, partial=True)
        if request.user in board.allowed_users:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, **kwargs):
        """
        Delete board
        """
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board: Board = get_object_or_404(Board, pk=pk)
        if request.user in board.allowed_users:
            board.delete()
            return Response({
                'success': True,
                'url': reverse_lazy('project_manager:project_detail', args=[project.id])
            })
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class BoardLastUpdatedAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a board instance.
    """

    def get(self, request, pk, **kwargs):
        """
        Retrive timestamps of last updated card and board
        """
        board: Board = get_object_or_404(Board, pk=pk)
        if request.user in board.allowed_users:
            board_timestamp = board.updated_at
            buckets_timestamp = [{'id': b.id, 'ts': b.updated_at} for b in board.bucket_set.all()]
            return Response({
                'board': board_timestamp,
                'buckets': buckets_timestamp
            })
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class BoardCalendarAPIView(LoginRequiredMixin, APIView):
    """
    List all cards from a board and filter by year and date of due date.
    """

    def get(self, request, **kwargs):
        """
        List cards from a board.
        """
        project_pk = kwargs.get('project_pk')
        board_pk = kwargs.get('pk')
        project = Project.objects.get(id=project_pk)
        board = Board.objects.get(project=project, id=board_pk)
        if request.user not in board.allowed_users:
            return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        cards = Card.objects.filter(bucket__board=board)
        if year and month:
            cards = cards.filter(
                due_date__year=year,
                due_date__month=month,
            )
        else:
            cards = cards.filter(
                due_date__isnull=True,
            )
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data)


class BucketListAPIView(LoginRequiredMixin, APIView):
    """
    List all buckets, or create a new bucket.
    """

    def get(self, request, **kwargs):
        """
        List all buckets in a board
        """
        board = Board.objects.get(id=kwargs['board_pk'])
        buckets = Bucket.objects.filter(board=board)
        if request.user in board.allowed_users:
            serializer = BucketSerializer(buckets, many=True, context={'request': request})
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def post(self, request, **kwargs):
        """
        Create new bucket
        """
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        serializer = BucketSerializer(data=request.data)
        if request.user not in board.allowed_users:
            return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        theme_id = request.data.get('color')
        color = Theme.objects.get(id=theme_id) if theme_id != '' else None
        serializer.save(
            created_by=request.user,
            order=board.max_order + 1,
            color=color,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BucketDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a bucket instance.
    """

    def get(self, request, pk, **kwargs):
        """
        Retrieve a bucket instance.
        """
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        bucket: Bucket = get_object_or_404(Bucket, pk=pk)
        if request.user in board.allowed_users:
            serializer = BucketSerializer(bucket)
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk, **kwargs):
        """
        Edit a bucket
        """
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        bucket: Bucket = get_object_or_404(Bucket, pk=pk)
        if request.user in board.allowed_users:
            serializer = BucketSerializer(bucket, data=request.data)
            if serializer.is_valid():
                serializer.save()
                theme_id = request.data.get('color')
                if theme_id in ['', None]:
                    bucket.color = None
                else:
                    color = Theme.objects.get(id=theme_id)
                    bucket.color = color
                bucket.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, **kwargs):
        """
        Delete a bucket instance.
        """
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        if request.user in board.allowed_users:
            bucket: Bucket = get_object_or_404(Bucket, pk=pk)
            bucket.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class TagListAPIView(LoginRequiredMixin, APIView):
    """
    List all tags, or create a new tag.
    """

    def get(self, request, **kwargs):
        """
        List all tags in a board.
        """
        board = Board.objects.get(id=kwargs['board_pk'])
        tags = Tag.objects.filter(board=board)
        if request.user in board.allowed_users:
            serializer = TagSerializer(tags, many=True, context={'request': request})
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def post(self, request, **kwargs):
        """
        Create a new tag.
        """
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        serializer = TagSerializer(data=request.data)
        if request.user in board.allowed_users:
            icon_id = request.data.get('icon')
            theme_id = request.data.get('color')
            if serializer.is_valid():
                extra_fields = {}
                if icon_id not in ['', None]:
                    icon = Icon.objects.get(id=int(icon_id))
                    extra_fields['icon'] = icon
                if theme_id not in ['', None]:
                    color = Theme.objects.get(id=int(theme_id))
                    extra_fields['color'] = color

                serializer.save(
                    board=board,
                    created_by=request.user,
                    **extra_fields
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class TagDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a tag instance.
    """

    def get(self, request, pk, **kwargs):
        """
        Retrieve a tag instance.
        """
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        tag: Tag = get_object_or_404(Tag, pk=pk)
        if request.user in board.allowed_users:
            serializer = TagSerializer(tag)
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk, **kwargs):
        """
        Edit tag
        """
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        tag: Tag = get_object_or_404(Tag, pk=pk)
        if request.user in board.allowed_users:
            icon_id = request.data.get('icon')
            serializer = TagSerializer(tag, data=request.data, context={'request': request})
            if serializer.is_valid():
                if icon_id not in ['', None]:
                    icon = Icon.objects.get(id=int(icon_id))
                    serializer.save(icon=icon)
                else:
                    serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, **kwargs):
        """
        Delete tag
        """
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        if request.user in board.allowed_users:
            tag: Tag = get_object_or_404(Tag, pk=pk)
            tag.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class CardListAPIView(LoginRequiredMixin, APIView):
    """
    List all cards, or create a new card.
    """

    def get(self, request, **kwargs):
        """
        List all cards
        """
        project_pk = kwargs.get('project_pk')
        board_pk = kwargs.get('board_pk')
        bucket_pk = kwargs.get('bucket_pk')
        project = Project.objects.get(id=project_pk)
        board = Board.objects.get(project=project, id=board_pk)
        bucket = Bucket.objects.get(board=board, id=bucket_pk)
        cards = Card.objects.filter(bucket=bucket)
        if request.user in board.allowed_users:
            serializer = CardSerializer(cards, many=True)
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def post(self, request, **kwargs):
        """
        Create new card
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        if request.user in board.allowed_users:
            serializer = CardSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                theme_id = request.data.get('color')
                if theme_id not in ['', None]:
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
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class CardDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a card instance.
    """

    def get(self, request, pk, **kwargs):
        """
        Retrieve a card instance
        """
        card: Card = get_object_or_404(Card, pk=pk)
        if request.user in card.allowed_users:
            serializer = CardSerializer(card)
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk, **kwargs):
        """
        Edit card
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        card: Card = get_object_or_404(Card, pk=pk)
        if request.user in card.allowed_users:
            serializer = CardSerializer(card, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                theme_id = request.data.get('color')
                if theme_id in ['', None]:
                    card.color = None
                else:
                    color = Theme.objects.get(id=theme_id)
                    card.color = color
                card.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk, **kwargs):
        """
        Edit card
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        card: Card = get_object_or_404(Card, pk=pk)
        if request.user in card.allowed_users:
            serializer = CardSerializer(card, data=request.data, context={'request': request}, partial=True)
            if serializer.is_valid():
                serializer.save()
                card.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, **kwargs):
        """
        Delete card
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        card: Card = get_object_or_404(Card, pk=pk)
        if request.user in card.allowed_users:
            card.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class ItemListAPIView(LoginRequiredMixin, APIView):
    """
    List all items, or create a new item.
    """

    def get(self, request, **kwargs):
        """
        List all items in a card
        """
        project_pk = kwargs.get('project_pk')
        board_pk = kwargs.get('board_pk')
        bucket_pk = kwargs.get('bucket_pk')
        card_pk = kwargs.get('card_pk')
        project = Project.objects.get(id=project_pk)
        board = Board.objects.get(project=project, id=board_pk)
        bucket = Bucket.objects.get(board=board, id=bucket_pk)
        card = Card.objects.get(bucket=bucket, id=card_pk)
        items = Item.objects.filter(card=card)
        if request.user in board.allowed_users:
            serializer = ItemSerializer(items, many=True)
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def post(self, request, **kwargs):
        """
        Create new card item
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        card = Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        if request.user in card.allowed_users:
            serializer = ItemSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(
                    created_by=request.user,
                    order=card.max_order + 1,
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class ItemDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete an item instance.
    """

    def get(self, request, pk, **kwargs):
        """
        Retrive a card item
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        item: Item = get_object_or_404(Item, pk=pk)
        if request.user in item.allowed_users:
            serializer = ItemSerializer(item)
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk, **kwargs):
        """
        Edit card item
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        item: Item = get_object_or_404(Item, pk=pk)
        if request.user in item.allowed_users:
            serializer = ItemSerializer(item, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk, **kwargs):
        """
        Edit card item
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        item: Item = get_object_or_404(Item, pk=pk)
        if request.user in item.allowed_users:
            serializer = ItemSerializer(item, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, **kwargs):
        """
        Delete card item
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        item: Item = get_object_or_404(Item, pk=pk)
        if request.user in item.allowed_users:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class CardFileListAPIView(LoginRequiredMixin, APIView):
    """
    List all card files, or create a new card file.
    """

    def get(self, request, **kwargs):
        """
        List card files in a card
        """
        project_pk = kwargs.get('project_pk')
        board_pk = kwargs.get('board_pk')
        bucket_pk = kwargs.get('bucket_pk')
        card_pk = kwargs.get('card_pk')
        project = Project.objects.get(id=project_pk)
        board = Board.objects.get(project=project, id=board_pk)
        bucket = Bucket.objects.get(board=board, id=bucket_pk)
        card = Card.objects.get(bucket=bucket, id=card_pk)
        files = CardFile.objects.filter(card=card)
        if request.user in board.allowed_users:
            serializer = CardFileSerializer(files, many=True)
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def post(self, request, **kwargs):
        """
        Create new card file
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        card = Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        if request.user in card.allowed_users:
            serializer = CardFileSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(card=card)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class CardFileDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete an card file instance.
    """

    def delete(self, request, pk, **kwargs):
        """
        Delete card file
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        file: CardFile = get_object_or_404(CardFile, pk=pk)
        if request.user in file.card.allowed_users:
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class TimeEntryListAPIView(LoginRequiredMixin, APIView):
    """
    List all time entries, or create a new time entry.
    """

    def get(self, request, **kwargs):
        """
        List all time entries
        """
        project_pk = kwargs.get('project_pk')
        board_pk = kwargs.get('board_pk')
        bucket_pk = kwargs.get('bucket_pk')
        card_pk = kwargs.get('card_pk')
        project = Project.objects.get(id=project_pk)
        board = Board.objects.get(project=project, id=board_pk)
        bucket = Bucket.objects.get(board=board, id=bucket_pk)
        card = Card.objects.get(bucket=bucket, id=card_pk)
        time_entries = TimeEntry.objects.filter(card=card)
        if request.user in board.allowed_users:
            serializer = TimeEntrySerializer(time_entries, many=True)
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def post(self, request, **kwargs):
        """
        Create new time entry
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        card = Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        if request.user in card.allowed_users:
            serializer = TimeEntrySerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(
                    created_by=request.user,
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class TimeEntryDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a time entry instance.
    """

    def get(self, request, pk, **kwargs):
        """
        Retrive time entry.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        time_entry: TimeEntry = get_object_or_404(TimeEntry, pk=pk)
        if request.user in time_entry.allowed_users:
            serializer = TimeEntrySerializer(time_entry)
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk, **kwargs):
        """
        Edit time entry.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        time_entry: TimeEntry = get_object_or_404(TimeEntry, pk=pk)
        if request.user in time_entry.allowed_users:
            serializer = TimeEntrySerializer(time_entry, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk, **kwargs):
        """
        Edit time entry partially.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        time_entry: TimeEntry = get_object_or_404(TimeEntry, pk=pk)
        if request.user in time_entry.allowed_users:
            serializer = TimeEntrySerializer(time_entry, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, **kwargs):
        """
        Delete time entry.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        time_entry: TimeEntry = get_object_or_404(TimeEntry, pk=pk)
        if request.user in time_entry.allowed_users:
            time_entry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class CommentListAPIView(LoginRequiredMixin, APIView):
    """
    List all comments, or create a new comment.
    """

    def get(self, request, **kwargs):
        """
        List all comments in a card.
        """
        project_pk = kwargs.get('project_pk')
        board_pk = kwargs.get('board_pk')
        bucket_pk = kwargs.get('bucket_pk')
        card_pk = kwargs.get('card_pk')
        project = Project.objects.get(id=project_pk)
        board = Board.objects.get(project=project, id=board_pk)
        bucket = Bucket.objects.get(board=board, id=bucket_pk)
        card = Card.objects.get(bucket=bucket, id=card_pk)
        comments = Comment.objects.filter(card=card)
        if request.user in board.allowed_users:
            serializer = CommentSerializer(comments, many=True)
            for comment in serializer.data:
                comment['created_at'] = NaturalTimeFormatter.string_for(
                    dateparse.parse_datetime(comment['created_at'])
                )
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def post(self, request, **kwargs):
        """
        Create new comment.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        card = Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        if request.user in card.allowed_users:
            serializer = CommentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(
                    created_by=request.user,
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class CommentDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete an comment instance.
    """

    def get(self, request, pk, **kwargs):
        """
        Retrive comment.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        comment: Comment = get_object_or_404(Comment, pk=pk)
        if request.user in comment.allowed_users:
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk, **kwargs):
        """
        Edit comment
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        comment: Comment = get_object_or_404(Comment, pk=pk)
        if request.user == comment.created_by:
            serializer = CommentSerializer(comment, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, **kwargs):
        """
        Delete comment.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        comment: Comment = get_object_or_404(Comment, pk=pk)
        if request.user == comment.created_by:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class ItemCheckAPIView(LoginRequiredMixin, APIView):
    """
    Mark an item instance as checked or unchecked.
    """

    def post(self, request, pk, **kwargs):
        """
        Toggle an item in a card.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        item: Item = get_object_or_404(Item, pk=pk)
        if request.user not in item.allowed_users:
            return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)
        if request.data.get('checked') == 'true':
            item.mark_as_checked(request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.data.get('checked') == 'false':
            item.mark_as_unchecked()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CardMoveApiView(LoginRequiredMixin, APIView):
    """
    Move card from one bucket to another bucket in given order.
    """

    def post(self, request):
        """
        Apply card move.
        """
        serializer = CardMoveSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.move()
            return Response(result)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BucketMoveApiView(LoginRequiredMixin, APIView):
    """
    Change bucket order in a board.
    """

    def post(self, request):
        """
        Apply bucket movement.
        """
        serializer = BucketMoveSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardMoveApiView(LoginRequiredMixin, APIView):
    """
    Change board order in a project.
    """

    def post(self, request):
        """
        Apply board movement.
        """
        serializer = BoardMoveSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StartStopTimerAPIView(LoginRequiredMixin, APIView):
    """
    Start or stop timer of a given card.
    """

    def post(self, request, pk, **kwargs):
        """
        Toggle timer on a card.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        card: Card = get_object_or_404(Card, pk=pk)
        if request.user in card.allowed_users:
            result = card.start_stop_timer(user=request.user)
            return Response({
                'success': True,
                'action': result['action']
            })
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class InviteListAPIView(LoginRequiredMixin, APIView):
    """
    List all invites, or create a new invite.
    """

    def get(self, request, **kwargs):
        """
        List all invites.
        """
        project_pk = kwargs.get('project_pk')
        project = Project.objects.get(id=project_pk)
        if request.user in project.allowed_users:
            invites = Invite.objects.filter(
                project=project,
                email__isnull=False,
            ).exclude(email__exact='')
            serializer = InviteSerializer(invites, many=True)
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def post(self, request, **kwargs):
        """
        Create new invite.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        serializer = InviteSerializer(data=request.data, context={'request': request})
        if request.user in project.allowed_users:
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class InviteDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete an invite instance.
    """

    def get(self, request, pk, **kwargs):
        """
        Retrieve invite information.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        if request.user in project.allowed_users:
            invite: Invite = get_object_or_404(Invite, pk=pk)
            serializer = InviteSerializer(invite)
            return Response(serializer.data)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk, **kwargs):
        """
        Edit invite.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        invite: Invite = get_object_or_404(Invite, pk=pk)
        if request.user in project.allowed_users:
            serializer = InviteSerializer(invite, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, **kwargs):
        """
        Delete invite.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        invite: Invite = get_object_or_404(Invite, pk=pk)
        if request.user in project.allowed_users:
            if invite.accepted:
                return Response('Cannot delete an accepted invite', status=status.HTTP_400_BAD_REQUEST)
            invite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)


class InviteResendAPIView(LoginRequiredMixin, APIView):
    """
    Resend invite email
    """

    def post(self, request, pk, **kwargs):
        """
        Create a new invite.
        """
        project = Project.objects.get(id=kwargs['project_pk'])
        invite: Invite = get_object_or_404(Invite, pk=pk)
        if request.user in project.allowed_users:
            invite.send()
            return Response({
                'success': True,
                'message': f'Your invitation was sent to {invite.email}.'
            }, status=status.HTTP_200_OK)
        return Response(_('User not allowed'), status=status.HTTP_403_FORBIDDEN)

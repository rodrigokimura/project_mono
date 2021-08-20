from datetime import date, datetime
from typing import Any, Optional
from django.conf import settings
from django.db.models.query import QuerySet
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.urls.base import reverse, reverse_lazy
from django.utils.timezone import is_aware, utc
from django.utils.translation import gettext_lazy, ngettext_lazy, npgettext_lazy
from django.template import defaultfilters
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.utils import dateparse
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from .models import Comment, Icon, Item, Project, Board, Bucket, Card, Tag, Theme, Invite
from .forms import ProjectForm, BoardForm
from .mixins import PassRequestToFormViewMixin
from .serializers import BucketMoveSerializer, CardMoveSerializer, CommentSerializer, InviteSerializer, ItemSerializer, ProjectSerializer, BoardSerializer, BucketSerializer, CardSerializer, TagSerializer


def naturaltime(value):
    """
    For date and time values show how many seconds, minutes, or hours ago
    compared to current timestamp return representing string.
    """
    return NaturalTimeFormatter.string_for(value)


class NaturalTimeFormatter:
    time_strings = {
        # Translators: delta will contain a string like '2 months' or '1 month, 2 weeks'
        'past-day': gettext_lazy('%(delta)s ago'),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        'past-hour': ngettext_lazy('an hour ago', '%(count)s hours ago', 'count'),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        'past-minute': ngettext_lazy('a minute ago', '%(count)s minutes ago', 'count'),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        'past-second': ngettext_lazy('a second ago', '%(count)s seconds ago', 'count'),
        'now': gettext_lazy('now'),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        'future-second': ngettext_lazy('a second from now', '%(count)s seconds from now', 'count'),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        'future-minute': ngettext_lazy('a minute from now', '%(count)s minutes from now', 'count'),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        'future-hour': ngettext_lazy('an hour from now', '%(count)s hours from now', 'count'),
        # Translators: delta will contain a string like '2 months' or '1 month, 2 weeks'
        'future-day': gettext_lazy('%(delta)s from now'),
    }
    past_substrings = {
        # Translators: 'naturaltime-past' strings will be included in '%(delta)s ago'
        'year': npgettext_lazy('naturaltime-past', '%d year', '%d years'),
        'month': npgettext_lazy('naturaltime-past', '%d month', '%d months'),
        'week': npgettext_lazy('naturaltime-past', '%d week', '%d weeks'),
        'day': npgettext_lazy('naturaltime-past', '%d day', '%d days'),
        'hour': npgettext_lazy('naturaltime-past', '%d hour', '%d hours'),
        'minute': npgettext_lazy('naturaltime-past', '%d minute', '%d minutes'),
    }
    future_substrings = {
        # Translators: 'naturaltime-future' strings will be included in '%(delta)s from now'
        'year': npgettext_lazy('naturaltime-future', '%d year', '%d years'),
        'month': npgettext_lazy('naturaltime-future', '%d month', '%d months'),
        'week': npgettext_lazy('naturaltime-future', '%d week', '%d weeks'),
        'day': npgettext_lazy('naturaltime-future', '%d day', '%d days'),
        'hour': npgettext_lazy('naturaltime-future', '%d hour', '%d hours'),
        'minute': npgettext_lazy('naturaltime-future', '%d minute', '%d minutes'),
    }

    @classmethod
    def string_for(cls, value):
        if not isinstance(value, date):  # datetime is a subclass of date
            return value

        now = datetime.now(utc if is_aware(value) else None)
        if value < now:
            delta = now - value
            if delta.days != 0:
                return cls.time_strings['past-day'] % {
                    'delta': defaultfilters.timesince(value, now, time_strings=cls.past_substrings),
                }
            elif delta.seconds == 0:
                return cls.time_strings['now']
            elif delta.seconds < 60:
                return cls.time_strings['past-second'] % {'count': delta.seconds}
            elif delta.seconds // 60 < 60:
                count = delta.seconds // 60
                return cls.time_strings['past-minute'] % {'count': count}
            else:
                count = delta.seconds // 60 // 60
                return cls.time_strings['past-hour'] % {'count': count}
        else:
            delta = value - now
            if delta.days != 0:
                return cls.time_strings['future-day'] % {
                    'delta': defaultfilters.timeuntil(value, now, time_strings=cls.future_substrings),
                }
            elif delta.seconds == 0:
                return cls.time_strings['now']
            elif delta.seconds < 60:
                return cls.time_strings['future-second'] % {'count': delta.seconds}
            elif delta.seconds // 60 < 60:
                count = delta.seconds // 60
                return cls.time_strings['future-minute'] % {'count': count}
            else:
                count = delta.seconds // 60 // 60
                return cls.time_strings['future-hour'] % {'count': count}


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

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        board = self.get_object()
        if request.user in board.allowed_users:
            return super().get(request, *args, **kwargs)
        else:
            messages.error(request, 'You are not assigned to this board!')
            return redirect(to=reverse('project_manager:project_detail', args=[board.project.id]))

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
        context['icons'] = Icon.objects.all()
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
    List all projects, or create a new project.
    """

    def get(self, request, format=None):
        projects = Project.objects.filter(created_by=request.user)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a project instance.
    """

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        if request.user in project.allowed_users:
            serializer = ProjectSerializer(project)
            return Response(serializer.data)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk, format=None):
        project = self.get_object(pk)
        if request.user in project.allowed_users:
            serializer = ProjectSerializer(project, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, format=None, **kwargs):
        project = self.get_object(pk)
        if request.user in project.allowed_users:
            project.delete()
            return Response({
                'success': True,
                'url': reverse_lazy('project_manager:projects')
            })
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class BoardListAPIView(LoginRequiredMixin, APIView):
    """
    List all projects, or create a new project.
    """

    def get(self, request, format=None, **kwargs):
        boards = Board.objects.filter(created_by=request.user)
        project = Project.objects.get(id=kwargs.get('project_pk'))
        if request.user in project.allowed_users:
            serializer = BoardSerializer(boards, many=True)
            return Response(serializer.data)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def post(self, request, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        serializer = BoardSerializer(data=request.data)
        if request.user in project.allowed_users:
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class BoardDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a board instance.
    """

    def get_object(self, pk):
        try:
            return Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None, **kwargs):
        board = self.get_object(pk)
        if request.user in board.allowed_users:
            serializer = BoardSerializer(board)
            return Response(serializer.data)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk, format=None, **kwargs):
        board = self.get_object(pk)
        serializer = BoardSerializer(board, data=request.data)
        if request.user in board.allowed_users:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk, format=None, **kwargs):
        board = self.get_object(pk)
        serializer = BoardSerializer(board, data=request.data, partial=True)
        if request.user in board.allowed_users:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = self.get_object(pk)
        if request.user in board.allowed_users:
            board.delete()
            return Response({
                'success': True,
                'url': reverse_lazy('project_manager:project_detail', args=[project.id])
            })
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


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
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

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
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class BucketDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a bucket instance.
    """

    def get_object(self, pk):
        try:
            return Bucket.objects.get(pk=pk)
        except Bucket.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        bucket = self.get_object(pk)
        if request.user in board.allowed_users:
            serializer = BucketSerializer(bucket)
            return Response(serializer.data)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        bucket = self.get_object(pk)
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
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        if request.user in board.allowed_users:
            bucket = self.get_object(pk)
            bucket.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class TagListAPIView(LoginRequiredMixin, APIView):
    """
    List all tags, or create a new tag.
    """

    def get(self, request, format=None, **kwargs):
        board = Board.objects.get(id=kwargs['board_pk'])
        tags = Tag.objects.filter(board=board)
        if request.user in board.allowed_users:
            serializer = TagSerializer(tags, many=True, context={'request': request})
            return Response(serializer.data)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def post(self, request, format=None, **kwargs):
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
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class TagDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a tag instance.
    """

    def get_object(self, pk):
        try:
            return Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        tag = self.get_object(pk)
        if request.user in board.allowed_users:
            serializer = TagSerializer(tag)
            return Response(serializer.data)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        tag = self.get_object(pk)
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
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs.get('project_pk'))
        board = Board.objects.get(project=project, id=kwargs.get('board_pk'))
        if request.user in board.allowed_users:
            tag = self.get_object(pk)
            tag.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class CardListAPIView(LoginRequiredMixin, APIView):
    """
    List all cards, or create a new card.
    """

    def get(self, request, format=None, **kwargs):
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
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

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
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class CardDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a card instance.
    """

    def get_object(self, pk):
        try:
            return Card.objects.get(pk=pk)
        except Card.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None, **kwargs):
        card = self.get_object(pk)
        if request.user in card.allowed_users:
            serializer = CardSerializer(card)
            return Response(serializer.data)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

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
                if theme_id in ['', None]:
                    card.color = None
                else:
                    color = Theme.objects.get(id=theme_id)
                    card.color = color
                card.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        card = self.get_object(pk)
        if request.user in card.allowed_users:
            card.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class ItemListAPIView(LoginRequiredMixin, APIView):
    """
    List all items, or create a new item.
    """

    def get(self, request, format=None, **kwargs):
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
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def post(self, request, format=None, **kwargs):
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
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class ItemDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete an item instance.
    """

    def get_object(self, pk):
        try:
            return Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        item = self.get_object(pk)
        if request.user in item.allowed_users:
            serializer = ItemSerializer(item)
            return Response(serializer.data)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        item = self.get_object(pk)
        if request.user in item.allowed_users:
            serializer = ItemSerializer(item, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        item = self.get_object(pk)
        if request.user in item.allowed_users:
            serializer = ItemSerializer(item, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        item = self.get_object(pk)
        if request.user in item.allowed_users:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class CommentListAPIView(LoginRequiredMixin, APIView):
    """
    List all comments, or create a new comment.
    """

    def get(self, request, format=None, **kwargs):
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
            data = serializer.data
            for c in data:
                c['created_at'] = naturaltime(
                    dateparse.parse_datetime(c['created_at'])
                )
            return Response(data)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def post(self, request, format=None, **kwargs):
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
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class CommentDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete an comment instance.
    """

    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        comment = self.get_object(pk)
        if request.user in comment.allowed_users:
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        comment = self.get_object(pk)
        if request.user == comment.created_by:
            serializer = CommentSerializer(comment, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        comment = self.get_object(pk)
        if request.user == comment.created_by:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class ItemCheckAPIView(LoginRequiredMixin, APIView):
    """
    Mark an item instance as checked or unchecked.
    """

    def get_object(self, pk):
        try:
            return Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            raise Http404

    def post(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        board = Board.objects.get(id=kwargs['board_pk'], project=project)
        bucket = Bucket.objects.get(id=kwargs['bucket_pk'], board=board)
        Card.objects.get(id=kwargs['card_pk'], bucket=bucket)
        item = self.get_object(pk)
        if request.user in item.allowed_users:
            if request.data.get('checked') == 'true':
                item.mark_as_checked(request.user)
                return Response(status=status.HTTP_204_NO_CONTENT)
            elif request.data.get('checked') == 'false':
                item.mark_as_unchecked()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


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
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


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
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def post(self, request, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        serializer = InviteSerializer(data=request.data, context={'request': request})
        if request.user in project.allowed_users:
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


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
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        invite = self.get_object(pk)
        if request.user in project.allowed_users:
            serializer = InviteSerializer(invite, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, format=None, **kwargs):
        project = Project.objects.get(id=kwargs['project_pk'])
        invite = self.get_object(pk)
        if request.user in project.allowed_users:
            invite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

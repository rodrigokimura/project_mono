"""Watcher's views"""
from __mono.permissions import IsCreator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Issue, Request
from .serializers import IssueIgnorerSerializer, IssueResolverSerializer


class RootView(UserPassesTestMixin, TemplateView):
    """
    Root view
    """
    template_name = "watcher/index.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        """
        Add extra context
        """
        context = super().get_context_data(**kwargs)
        context['unresolved_issues'] = Issue.objects.filter(resolved_at__isnull=True)
        context['resolved_issues'] = Issue.objects.exclude(resolved_at__isnull=True)
        context['requests'] = Request.objects.all()
        requests_by_app = [
            {
                'app_name': result['app_name'],
                'avg': round(result['avg'].total_seconds() * 1000, 2)
            }
            for result in Request.objects.values('app_name').annotate(avg=Avg('duration'))
        ]
        context['requests_by_app'] = requests_by_app
        return context

    def dispatch(self, *args, **kwargs):
        """
        Add headers to avoid bf-cache
        """
        response = super().dispatch(*args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response


class IssueDetailView(UserPassesTestMixin, DetailView):
    model = Issue

    def test_func(self):
        return self.request.user.is_superuser


class IssueResolveAPIView(LoginRequiredMixin, APIView):
    """
    Mark issue as resolved
    """

    permission_classes = [IsCreator, IsAdminUser]

    def post(self, request, pk, **kwargs):
        """
        Mark issue as resolved
        """
        issue = get_object_or_404(Issue, pk=pk)
        serializer = IssueResolverSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.data['resolved']:
            issue.resolve(request.user)
        else:
            issue.unresolve()
        return Response({'success': True})


class IssueIgnoreAPIView(LoginRequiredMixin, APIView):
    """
    Mark issue as ignored
    """

    permission_classes = [IsCreator, IsAdminUser]

    def post(self, request, pk, **kwargs):
        """
        Mark issue as ignored
        """
        issue = get_object_or_404(Issue, pk=pk)
        serializer = IssueIgnorerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.data['ignored']:
            issue.ignore(request.user)
        else:
            issue.unignore()
        return Response({'success': True})

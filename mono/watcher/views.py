"""Watcher's views"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Issue
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


class IssueDetailView(DetailView):
    model = Issue


class IssueResolveAPIView(LoginRequiredMixin, APIView):
    """
    Mark issue as resolved
    """

    def post(self, request, pk, **kwargs):
        """
        Mark issue as resolved
        """
        issue = get_object_or_404(Issue, pk=pk)
        if not request.user.is_superuser:
            return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)
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
    def post(self, request, pk, **kwargs):
        """
        Mark issue as ignored
        """
        issue = get_object_or_404(Issue, pk=pk)
        if not request.user.is_superuser:
            return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)
        serializer = IssueIgnorerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.data['ignored']:
            issue.ignore(request.user)
        else:
            issue.unignore()
        return Response({'success': True})

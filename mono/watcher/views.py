
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Issue
from .serializers import IssueIgnorerSerializer, IssueResolverSerializer


class RootView(UserPassesTestMixin, TemplateView):
    template_name = "watcher/index.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unresolved_issues'] = Issue.objects.filter(resolved_at__isnull=True)
        context['resolved_issues'] = Issue.objects.exclude(resolved_at__isnull=True)
        return context

    def dispatch(self, *args, **kwargs):
        # avoid bfcache
        response = super().dispatch(*args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response


class IssueDetailView(DetailView):
    model = Issue


def get_issue(pk):
    try:
        return Issue.objects.get(pk=pk)
    except Issue.DoesNotExist:
        raise Http404


class IssueResolveAPIView(LoginRequiredMixin, APIView):

    def post(self, request, pk, format=None, **kwargs):
        issue: Issue = get_issue(pk)
        if request.user.is_superuser:
            serializer = IssueResolverSerializer(data=request.data)
            if serializer.is_valid():
                if serializer.data['resolved']:
                    issue.resolve(request.user)
                else:
                    issue.unresolve()
                return Response({'success': True})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class IssueIgnoreAPIView(LoginRequiredMixin, APIView):

    def post(self, request, pk, format=None, **kwargs):
        issue: Issue = get_issue(pk)
        if request.user.is_superuser:
            serializer = IssueIgnorerSerializer(data=request.data)
            if serializer.is_valid():
                if serializer.data['ignored']:
                    issue.ignore(request.user)
                else:
                    issue.unignore()
                return Response({'success': True})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

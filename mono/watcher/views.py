
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Issue
from .serializers import IssueResolverSerializer


class RootView(UserPassesTestMixin, TemplateView):
    template_name = "watcher/index.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # a = 1 / 0
        # test
        context['unresolved_issues'] = Issue.objects.filter(resolved_at__isnull=True)
        context['resolved_issues'] = Issue.objects.exclude(resolved_at__isnull=True)
        return context


class IssueDetailView(DetailView):
    model = Issue


class IssueResolveAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete a card instance.
    """

    def get_object(self, pk):
        try:
            return Issue.objects.get(pk=pk)
        except Issue.DoesNotExist:
            raise Http404

    def post(self, request, pk, format=None, **kwargs):
        issue: Issue = self.get_object(pk)
        if request.user.is_superuser:
            serializer = IssueResolverSerializer(data=request.data)
            if serializer.is_valid():
                issue.resolve(request.user)
                return Response({'success': True})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)

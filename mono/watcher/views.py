
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from .models import Issue


class RootView(UserPassesTestMixin, TemplateView):
    template_name = "watcher/index.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # a = 1 / 0
        # test
        context['issues'] = Issue.objects.all()
        return context


class IssueDetailView(DetailView):
    model = Issue

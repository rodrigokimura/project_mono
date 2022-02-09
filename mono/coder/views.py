"""Coder's views"""
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from pygments.formatters import \
    HtmlFormatter  # pylint: disable=no-name-in-module

from .models import Snippet


class RootView(TemplateView):
    """
    App's first view.
    """
    template_name = "coder/index.html"


class SnippetListView(ListView):
    """
    List of user's snippets.
    """
    model = Snippet
    paginate_by = 20
    template_name = 'coder/snippet_list.html'

    def get_queryset(self):
        return Snippet.objects.filter(created_by=self.request.user)


class SnippetDetailView(DetailView):
    """
    Snippet detail view.
    """
    model = Snippet
    template_name = 'coder/snippet_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['css'] = str(HtmlFormatter().get_style_defs('.highlight'))
        return context

class SnippetEditView(DetailView):
    """
    Snippet edit view.
    """
    model = Snippet
    template_name = 'coder/snippet_edit.html'

"""Coder's views"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from pygments.formatters import \
    HtmlFormatter  # pylint: disable=no-name-in-module

from .models import Configuration, Snippet, LANGUAGE_CHOICES


class RootView(TemplateView):
    """
    App's first view.
    """
    template_name = "coder/index.html"


class SnippetListView(LoginRequiredMixin, TemplateView):
    """
    List of user's snippets.
    """
    template_name = 'coder/snippet_list.html'

    def get_queryset(self):
        return Snippet.objects.filter(created_by=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['languages'] = LANGUAGE_CHOICES
        config: Configuration = Configuration.objects.get_or_create(user = self.request.user)[0]
        context['snippet_css'] = HtmlFormatter(style=config.style).get_style_defs('.highlight')
        # context['snippet_css'] = HtmlFormatter(style=config.style)
        return context


class SnippetEditView(DetailView):
    """
    Snippet edit view.
    """
    model = Snippet
    template_name = 'coder/snippet_edit.html'

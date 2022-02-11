"""Coder's views"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from pygments.formatters import \
    HtmlFormatter  # pylint: disable=no-name-in-module

from .models import LANGUAGE_CHOICES, Configuration, Snippet


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
        config: Configuration = Configuration.objects.get_or_create(user=self.request.user)[0]
        context['snippet_css'] = HtmlFormatter(style=config.style).get_style_defs('.highlight')
        return context


class SnippetEditView(DetailView):
    """
    Snippet edit view.
    """
    model = Snippet
    template_name = 'coder/snippet_edit.html'


class SnippetPublicView(TemplateView):
    """
    Snippet public view.
    """
    template_name = 'coder/snippet_public.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        snippet = get_object_or_404(Snippet, public_id=kwargs.get('public_id'))
        if not snippet.public:
            raise Http404
        context['snippet'] = snippet
        context['snippet_css'] = HtmlFormatter(style='monokai').get_style_defs('.highlight')
        return context

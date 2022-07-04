"""Coder's views"""
from __mono.permissions import IsCreator
from __mono.utils import Color
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from pygments import highlight
from pygments.formatters import \
    HtmlFormatter  # pylint: disable=no-name-in-module
from pygments.lexers import get_lexer_by_name
from rest_framework.generics import RetrieveUpdateAPIView

from .models import LANGUAGE_CHOICES, STYLE_CHOICES, Configuration, Snippet
from .serializers import ConfigurationSerializer


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
        code = [
            'def fib(n):',
            '   """Print Fibonacci sequence"""',
            '    a, b = 0, 1',
            '    while a < n:',
            '        print(a, end=\' \')',
            '        a, b = b, a + b',
            'fib(1000)',
        ]
        context = super().get_context_data(*args, **kwargs)
        context['languages'] = LANGUAGE_CHOICES
        context['styles'] = STYLE_CHOICES
        context['colors'] = Color.choices
        context['all_styles_css'] = ''.join(
            HtmlFormatter(style=style[0]).get_style_defs(f'.{style[0]}')
            for style in STYLE_CHOICES
        )
        context['demo_code'] = highlight(
            '\n'.join(code),
            lexer=get_lexer_by_name('python', stripall=True),
            formatter=HtmlFormatter(linenos=True),
        )
        return context


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


class ConfigAPIView(RetrieveUpdateAPIView):
    """View to read or update user config"""

    serializer_class = ConfigurationSerializer
    permission_classes = [IsCreator]

    def get_object(self):
        return Configuration.objects.get_or_create(created_by=self.request.user)[0]

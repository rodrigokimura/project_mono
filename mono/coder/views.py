"""Coder's views"""
from __mono.permissions import IsCreator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from pygments import highlight
from pygments.formatters import \
    HtmlFormatter  # pylint: disable=no-name-in-module
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.styles import get_all_styles

from .models import LANGUAGE_CHOICES, Configuration, Snippet, Tag
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
        context = super().get_context_data(*args, **kwargs)
        context['languages'] = LANGUAGE_CHOICES
        context['colors'] = Tag.Color.choices
        config: Configuration = Configuration.objects.get_or_create(created_by=self.request.user)[0]
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


class ConfigAPIView(RetrieveUpdateAPIView):
    """View to read or update user config"""

    serializer_class = ConfigurationSerializer

    def get_object(self):
        return Configuration.objects.get_or_create(created_by=self.request.user)[0]


class DemoAPIView(APIView):

    def get(self, request):
        linenos = request.query_params.get('linenos', True)
        style = request.query_params.get('style', 'monokai')

        code = """
            def fib(n):
                a, b = 0, 1
                while a < n:
                    print(a, end=' ')
                    a, b = b, a+b
                    print()
            
            fib(1000)
        """

        lexer = get_lexer_by_name('python', stripall=True)
        formatter = HtmlFormatter(
            linenos=linenos,
            style=style
        )
        css = HtmlFormatter(style=style).get_style_defs('.demo')
        html = highlight(code, lexer, formatter)
        return Response(
            f"""<style>{css}</style>
            <div class="demo">{html}</div>"""
        )

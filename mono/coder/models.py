"""Coder's models"""
from django.contrib.auth import get_user_model
from django.db import models
from ordered_model.models import OrderedModel
from pygments import highlight
from pygments.formatters import \
    HtmlFormatter  # pylint: disable=no-name-in-module
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

User = get_user_model()


class BaseModel(models.Model):
    """Abstract model for this app"""
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Snippet(BaseModel, OrderedModel):
    """Store snippets of code"""
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)

    order_with_respect_to = 'created_by'

    @property
    def html(self):
        """Output code in formatted html"""
        lexer = get_lexer_by_name(self.language, stripall=True)
        formatter = HtmlFormatter(
            linenos=self.linenos,
            style=self.style
        )
        return highlight(self.code, lexer, formatter)

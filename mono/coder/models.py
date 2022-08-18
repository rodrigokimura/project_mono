"""Coder's models"""
import uuid

from __mono.utils import Color
from django.contrib.auth import get_user_model
from django.db import models
from ordered_model.models import OrderedModel
from pygments import highlight
from pygments.formatters import (
    HtmlFormatter,  # pylint: disable=no-name-in-module
)
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


class Tag(BaseModel, OrderedModel):
    """Store tags"""

    name = models.CharField(max_length=100, blank=True, default="")
    color = models.CharField(
        choices=Color.choices, default=Color.BLUE.value, max_length=100
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="coder_tags"
    )

    order_with_respect_to = "created_by"

    def __str__(self) -> str:
        return f"#{self.name}"


class Snippet(BaseModel, OrderedModel):
    """Store snippets of code"""

    title = models.CharField(max_length=100, blank=True, default="")
    code = models.TextField()
    language = models.CharField(
        choices=LANGUAGE_CHOICES, default="python", max_length=100
    )
    public_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    public = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True)

    order_with_respect_to = "created_by"

    def __str__(self) -> str:
        return self.title

    @property
    def html(self):
        """Output code in formatted html"""
        lexer = get_lexer_by_name(self.language, stripall=True)
        config = Configuration.objects.get_or_create(
            created_by=self.created_by
        )[0]
        formatter = HtmlFormatter(linenos=config.linenos, style=config.style)
        return highlight(self.code, lexer, formatter)


class Configuration(models.Model):
    """Store user configuration"""

    style = models.CharField(
        choices=STYLE_CHOICES, default="monokai", max_length=100
    )
    linenos = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="coder_config"
    )

"""Utility functions for the application."""
import logging
from importlib import import_module

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def validate_file_size(file, size):
    """Validate file size."""
    if file.size > size * 1024 * 1024:
        raise ValidationError(f"Max size of file is {size} MiB")
    return file


def load_signals(app: str):
    """Load app's signals by dynamic import."""
    import_module(f'{app}.signals')
    logger.info('Loading signals from %s app', app)


class Color(models.TextChoices):
    """Semantic UI color choices"""
    RED = 'red', _('Red')
    ORANGE = 'orange', _('Orange')
    YELLOW = 'yellow', _('Yellow')
    OLIVE = 'olive', _('Olive')
    GREEN = 'green', _('Green')
    TEAL = 'teal', _('Teal')
    BLUE = 'blue', _('Blue')
    VIOLET = 'violet', _('Violet')
    PURPLE = 'purple', _('Purple')
    PINK = 'pink', _('Pink')
    BROWN = 'brown', _('Brown')
    GREY = 'grey', _('Grey')
    BLACK = 'black', _('Black')

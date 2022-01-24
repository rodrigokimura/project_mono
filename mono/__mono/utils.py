"""Utility functions for the application."""
import logging
from importlib import import_module

from django.core.exceptions import ValidationError

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

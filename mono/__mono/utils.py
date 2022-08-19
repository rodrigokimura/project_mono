"""Utility functions for the application."""
import logging
from datetime import date, datetime, timezone
from importlib import import_module

from django.core.exceptions import ValidationError
from django.db import models
from django.template import defaultfilters
from django.utils.timezone import is_aware
from django.utils.translation import gettext_lazy, ngettext_lazy, npgettext_lazy

logger = logging.getLogger(__name__)


def validate_file_size(file, size):
    """Validate file size."""
    if file.size > size * 1024 * 1024:
        raise ValidationError(f"Max size of file is {size} MiB")
    return file


def load_signals(app: str):
    """Load app's signals by dynamic import."""
    import_module(f"{app}.signals")
    logger.info("Loading signals from %s app", app)


class Color(models.TextChoices):
    """Semantic UI color choices"""

    RED = "red", gettext_lazy("Red")
    ORANGE = "orange", gettext_lazy("Orange")
    YELLOW = "yellow", gettext_lazy("Yellow")
    OLIVE = "olive", gettext_lazy("Olive")
    GREEN = "green", gettext_lazy("Green")
    TEAL = "teal", gettext_lazy("Teal")
    BLUE = "blue", gettext_lazy("Blue")
    VIOLET = "violet", gettext_lazy("Violet")
    PURPLE = "purple", gettext_lazy("Purple")
    PINK = "pink", gettext_lazy("Pink")
    BROWN = "brown", gettext_lazy("Brown")
    GREY = "grey", gettext_lazy("Grey")
    BLACK = "black", gettext_lazy("Black")


class NaturalTimeFormatter:
    """
    Simple class to format datetimes to human-readable timeintervals
    """

    time_strings = {
        # Translators: delta will contain a string like '2 months' or '1 month, 2 weeks'
        "past-day": gettext_lazy("%(delta)s ago"),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        "past-hour": ngettext_lazy(
            "an hour ago", "%(count)s hours ago", "count"
        ),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        "past-minute": ngettext_lazy(
            "a minute ago", "%(count)s minutes ago", "count"
        ),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        "past-second": ngettext_lazy(
            "a second ago", "%(count)s seconds ago", "count"
        ),
        "now": gettext_lazy("now"),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        "future-second": ngettext_lazy(
            "a second from now", "%(count)s seconds from now", "count"
        ),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        "future-minute": ngettext_lazy(
            "a minute from now", "%(count)s minutes from now", "count"
        ),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        "future-hour": ngettext_lazy(
            "an hour from now", "%(count)s hours from now", "count"
        ),
        # Translators: delta will contain a string like '2 months' or '1 month, 2 weeks'
        "future-day": gettext_lazy("%(delta)s from now"),
    }
    past_substrings = {
        # Translators: 'naturaltime-past' strings will be included in '%(delta)s ago'
        "year": npgettext_lazy("naturaltime-past", "%d year", "%d years"),
        "month": npgettext_lazy("naturaltime-past", "%d month", "%d months"),
        "week": npgettext_lazy("naturaltime-past", "%d week", "%d weeks"),
        "day": npgettext_lazy("naturaltime-past", "%d day", "%d days"),
        "hour": npgettext_lazy("naturaltime-past", "%d hour", "%d hours"),
        "minute": npgettext_lazy("naturaltime-past", "%d minute", "%d minutes"),
    }
    future_substrings = {
        # Translators: 'naturaltime-future' strings will be included in '%(delta)s from now'
        "year": npgettext_lazy("naturaltime-future", "%d year", "%d years"),
        "month": npgettext_lazy("naturaltime-future", "%d month", "%d months"),
        "week": npgettext_lazy("naturaltime-future", "%d week", "%d weeks"),
        "day": npgettext_lazy("naturaltime-future", "%d day", "%d days"),
        "hour": npgettext_lazy("naturaltime-future", "%d hour", "%d hours"),
        "minute": npgettext_lazy(
            "naturaltime-future", "%d minute", "%d minutes"
        ),
    }

    @classmethod
    def string_for(cls, value):
        """Get formatted string"""
        if not isinstance(value, date):  # datetime is a subclass of date
            return value

        now = datetime.now(timezone.utc if is_aware(value) else None)
        is_past = value < now
        if is_past:
            delta = now - value
        else:
            delta = value - now
        return cls.get_string(now, value, delta, is_past)

    @classmethod
    def get_string(cls, now, value, delta, is_past: bool):
        """Split logic between past or future values"""
        time = "past" if is_past else "future"
        if delta.days != 0:
            return cls.time_strings[f"{time}-day"] % {
                "delta": defaultfilters.timesince(
                    value, now, time_strings=cls.past_substrings
                ),
            }
        if delta.seconds == 0:
            return cls.time_strings["now"]
        if delta.seconds < 60:
            return cls.time_strings[f"{time}-second"] % {"count": delta.seconds}
        if delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return cls.time_strings[f"{time}-minute"] % {"count": count}
        count = delta.seconds // 60 // 60
        return cls.time_strings[f"{time}-hour"] % {"count": count}

"""Useful mixins"""
import uuid

from django.db import models


class PassRequestToFormViewMixin:  # pylint: disable=too-few-public-methods
    """Pass request to FormView subclass"""

    def get_form_kwargs(self):
        """Pass request to FormView subclass"""
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class PublicIDMixin(models.Model):
    """Generate a public_id field"""

    public_id = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False
    )

    class Meta:
        abstract = True

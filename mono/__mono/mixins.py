"""Useful mixins"""


class PassRequestToFormViewMixin:  # pylint: disable=too-few-public-methods
    """Pass request to FormView subclass"""
    def get_form_kwargs(self):
        """Pass request to FormView subclass"""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

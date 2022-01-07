from django.test import TestCase
from django.test.client import RequestFactory
from django.views.generic.edit import FormView

from .mixins import PassRequestToFormViewMixin


class MixinTests(TestCase):

    def test_pass_request_to_form_mixin(self):
        class CustomFormView(PassRequestToFormViewMixin, FormView):
            pass

        request = RequestFactory().get('/')
        view = CustomFormView()
        view.setup(request)
        kwargs = view.get_form_kwargs()
        self.assertIn('request', kwargs)

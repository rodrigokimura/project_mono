from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http.response import Http404, HttpResponse, JsonResponse, HttpResponseServerError

from django.views.generic.base import TemplateView, View

class IndexView(UserPassesTestMixin, TemplateView):
    
    template_name = 'restricted_area/index.html'

    def test_func(self):
        return self.request.user.is_superuser


class ForceError500View(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        raise Exception("Faking an error.")


class ViewError500View(UserPassesTestMixin, TemplateView):

    template_name = '500.html'

    def test_func(self):
        return self.request.user.is_superuser

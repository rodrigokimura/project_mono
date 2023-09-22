"""Homepage's views"""
from django.contrib.auth import views
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView


@method_decorator(cache_page(60 * 5), name="dispatch")
class Login(views.LoginView):
    template_name = "homepage/home.html"


@method_decorator(cache_page(60 * 5), name="dispatch")
class HomepageView(TemplateView):
    template_name = "homepage/home.html"

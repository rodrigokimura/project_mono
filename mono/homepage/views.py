"""Homepage's views"""
from django.contrib.auth import views
from django.views.generic.base import TemplateView


class Login(views.LoginView):
    template_name = "homepage/home.html"


class HomepageView(TemplateView):
    template_name = "homepage/home.html"

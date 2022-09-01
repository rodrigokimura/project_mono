"""Mind maps urls"""
from django.urls import path

from . import views

app_name = "mind_maps"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
]

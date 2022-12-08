"""Typer urls"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import LessonViewSet, RecordViewSet

app_name = "typer"

router = DefaultRouter()
router.register("lessons", LessonViewSet)
router.register("records", RecordViewSet)

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("lessons/", views.LessonListView.as_view(), name="lesson_list"),
    path("<uuid:pk>/", views.LessonDetailView.as_view(), name="detail"),
    # API urls
    path("api/", include(router.urls)),
]

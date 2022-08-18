"""Coder's urls"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import SnippetViewSet, TagViewSet

app_name = "coder"

router = DefaultRouter()
router.register("snippets", SnippetViewSet)
router.register("tags", TagViewSet)

urlpatterns = [
    path("", views.RootView.as_view(), name="index"),
    path("snippet/", views.SnippetListView.as_view(), name="snippet_list"),
    path(
        "snippet/<uuid:public_id>/",
        views.SnippetPublicView.as_view(),
        name="snippet_public",
    ),
    path("api/", include(router.urls)),
    path("api/config/", views.ConfigAPIView.as_view(), name="config"),
]

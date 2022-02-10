"""Coder's urls"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import SnippetViewSet

app_name = 'coder'

router = DefaultRouter()
router.register('snippets', SnippetViewSet)

# pylint: disable=C0301
urlpatterns = [
    path("", views.RootView.as_view(), name='index'),
    path("snippet/", views.SnippetListView.as_view(), name='snippet_list'),
    path("snippet/<int:pk>/edit/", views.SnippetEditView.as_view(), name='snippet_edit'),
    path("snippet/<uuid:public_id>/", views.SnippetPublicView.as_view(), name='snippet_public'),
    path("api/", include(router.urls))
]

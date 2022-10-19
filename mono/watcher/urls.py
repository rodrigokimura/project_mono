"""Watcher's urls"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import CommentViewSet, IssueViewSet, RequestViewSet

app_name = "watcher"

router = DefaultRouter()
router.register("comments", CommentViewSet)
router.register("issues", IssueViewSet)
router.register("requests", RequestViewSet)

urlpatterns = [
    path("", views.RootView.as_view(), name="index"),
    path(
        "issue/<int:pk>/", views.IssueDetailView.as_view(), name="issue_detail"
    ),
    path(
        "issue/<int:pk>/resolve/",
        views.IssueResolveAPIView.as_view(),
        name="issue_resolve",
    ),
    path(
        "issue/<int:pk>/ignore/",
        views.IssueIgnoreAPIView.as_view(),
        name="issue_ignore",
    ),
    path("api/", include(router.urls)),
]

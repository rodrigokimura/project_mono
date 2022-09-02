"""Mind maps urls"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import MindMapViewSet, NodeViewSet

app_name = "mind_maps"

router = DefaultRouter()
router.register("mind_maps", MindMapViewSet)
router.register("nodes", NodeViewSet)

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<uuid:pk>/", views.MindMapDetailView.as_view(), name="detail"),
    path("pg/", views.PlaygroundView.as_view(), name="playground"),
    # API urls
    path("api/", include(router.urls)),
]

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
    path("mind-maps/", views.MindMapListView.as_view(), name="mind_map_list"),
    path("<uuid:pk>/", views.MindMapDetailView.as_view(), name="detail"),
    path("<uuid:pk>/sync/", views.FullSyncView.as_view(), name="sync"),
    # API urls
    path("api/", include(router.urls)),
]

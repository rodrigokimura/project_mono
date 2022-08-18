"""Todo Lists' urls"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import ChecklistViewSet, TaskViewSet

app_name = "checklists"

router = DefaultRouter()
router.register("tasks", TaskViewSet)
router.register("checklists", ChecklistViewSet)


urlpatterns = [
    path("", views.HomePageView.as_view(), name="index"),
    # API urls
    path("api/", include(router.urls)),
    path("api/task-move/", views.TaskMoveApiView.as_view()),
    path("api/checklist-move/", views.ChecklistMoveApiView.as_view()),
    path("api/config/", views.ConfigAPIView.as_view(), name="config"),
]

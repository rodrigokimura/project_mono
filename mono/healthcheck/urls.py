"""Healthcheck's urls"""
from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "healthcheck"

router = routers.DefaultRouter()
router.register("pylint", views.PylintReportViewSet, basename="pylint")
router.register("pytest", views.PytestReportViewSet, basename="pytest")
router.register("coverage", views.CoverageReportViewSet, basename="coverage")


urlpatterns = [
    path("", views.healthcheck, name="healthcheck"),
    path("migrations/", views.ShowMigrationsView.as_view(), name="migrations"),
    path("home/", views.HealthcheckHomePage.as_view(), name="home"),
    path("update_app/", views.github_webhook, name="update_app"),
    path("deploy/", views.Deploy.as_view(), name="deploy"),
    path(
        "api/commits/by-date/",
        views.CommitsByDateView.as_view(),
        name="commits_by_date",
    ),
    path(
        "api/commits/for-heatmap/",
        views.CommitsFormattedForHeatmapView.as_view(),
        name="commits_for_heatmap",
    ),
    path("api/changelog/", views.ChangelogView.as_view(), name="changelog"),
    path("api/summary/", views.SummaryView.as_view(), name="summary"),
    path("api/", include(router.urls)),
]

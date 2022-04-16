"""Healthcheck's urls"""
from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'healthcheck'

router = routers.DefaultRouter()
router.register('pytest', views.PytestReportViewSet, basename='pytest')


urlpatterns = [
    path('', views.healthcheck, name='healthcheck'),
    path('home/', views.HealthcheckHomePage.as_view(), name='home'),
    path('update_app/', views.github_webhook, name='update_app'),
    path('deploy/', views.Deploy.as_view(), name='deploy'),
    path('api/commits/by-date/', views.CommitsByDateView.as_view(), name='commits_by_date'),
    path('api/commits/for-heatmap/', views.CommitsFormattedForHeatmapView.as_view(), name='commits_for_heatmap'),
    path('api/changelog/', views.ChangelogView.as_view(), name='changelog'),
    # path('api/pytest/', views.QualityCheckView.as_view(), name='pytest'),
    # path('api/pytest/', views.PytestReportView.as_view(), name='pytest'),
    path('api/', include(router.urls)),
]

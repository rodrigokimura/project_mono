from django.conf import settings
from django.urls import path

from . import views

app_name = 'pixel'

urlpatterns = [
    path('pixel.gif', views.pixel_gif, name='pixel_gif'),
    path('', views.RootView.as_view(), name='root'),
    path('tags/', views.SitesView.as_view(), name='tags'),
    path('tags/new/', views.SiteCreateView.as_view(), name='tag_create'),
    path('tags/<uuid:pk>/', views.SiteDetailApiView.as_view(), name='tag_detail'),
    path('dashboard/<uuid:pk>/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/<uuid:pk>/general-info/', views.DashboardGeneralInfoApiView.as_view()),
    path('dashboard/<uuid:pk>/by-date/', views.DashboardAggregatedByDateApiView.as_view()),
    path('dashboard/<uuid:pk>/by-doc-loc/', views.DashboardAggregatedByDocLocApiView.as_view()),
]

if settings.APP_ENV == 'DEV':
    urlpatterns += path('test', views.test, name='test'),

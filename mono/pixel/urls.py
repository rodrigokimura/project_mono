from django.urls import path
from django.conf import settings
from . import views

app_name = 'pixel'

urlpatterns = [
    path('pixel.gif', views.pixel_gif, name='pixel_gif'),
    path('', views.RootView.as_view(), name='root'),
    path('dashboard/<uuid:pk>', views.Dashboard.as_view(), name='dashboard'),
    path('dashboard/<uuid:pk>/general-info/', views.DashboardGeneralInfoApiView.as_view()),
    path('dashboard/<uuid:pk>/by-date/', views.DashboardAggregatedByDateApiView.as_view()),
    path('dashboard/<uuid:pk>/by-doc-loc/', views.DashboardAggregatedByDocLocApiView.as_view()),
]

if settings.APP_ENV == 'DEV':
    urlpatterns += path('test', views.test, name='test'),

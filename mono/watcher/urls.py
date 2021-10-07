from django.urls import path

from . import views

app_name = 'watcher'

urlpatterns = [
    path('', views.RootView.as_view(), name='index'),
    path('issue/<int:pk>/', views.IssueDetailView.as_view(), name='issue_detail'),
    path('issue/<int:pk>/resolve/', views.IssueResolveAPIView.as_view(), name='issue_resolve'),
]

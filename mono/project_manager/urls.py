from django.urls import path
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from . import views
from .viewsets import UserViewSet, BoardViewSet, ProjectViewSet


app_name = 'project_manager'

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('projects', ProjectViewSet)
router.register('boards', BoardViewSet)

urlpatterns = [

    path('', RedirectView.as_view(pattern_name='project_manager:projects'), name='index'),

    path('project/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('projects/', views.ProjectListView.as_view(), name='projects'),

    path('board/', views.BoardCreateView.as_view(), name='board_create'),
    path('board/<int:pk>/', views.BoardDetailView.as_view(), name='board_detail'),
    path('board/<int:pk>/edit/', views.BoardUpdateView.as_view(), name='board_update'),
    path('board/<int:pk>/delete/', views.BoardDeleteView.as_view(), name='board_delete'),
    path('boards/', views.BoardListView.as_view(), name='boards'),
]

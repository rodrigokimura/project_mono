from django.urls import path
from django.views.generic.base import RedirectView
from . import views

app_name = 'project_manager'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='project_manager:projects'), name='index'),
    path('project/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>', views.ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('projects/', views.ProjectListView.as_view(), name='projects'),
]

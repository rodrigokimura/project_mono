"""Todo Lists' urls"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import ChecklistViewSet, TaskViewSet

app_name = 'checklists'

router = DefaultRouter()
router.register('tasks', TaskViewSet)
router.register('checklists', ChecklistViewSet)


urlpatterns = [

    # path('', RedirectView.as_view(pattern_name='checklists:lists'), name='index'),
    path('', views.HomePageView.as_view(), name='index'),

    path('list/', views.ListCreateView.as_view(), name='list_create'),
    path('list/<int:pk>/edit/', views.ListUpdateView.as_view(), name='list_update'),
    path('list/<int:pk>/delete/', views.ListDeleteView.as_view(), name='list_delete'),

    # API urls
    path('api/', include(router.urls)),
    path('api/tasks/<int:pk>/check/', views.TaskCheckApiView.as_view(), name='api_tasks_check'),
    path('api/tasks/<int:pk>/uncheck/', views.TaskUncheckApiView.as_view(), name='api_tasks_uncheck'),
]

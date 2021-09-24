from django.urls import path

# from django.views.generic.base import RedirectView
from . import views

app_name = 'todo_lists'


urlpatterns = [

    # path('', RedirectView.as_view(pattern_name='todo_lists:lists'), name='index'),
    path('', views.HomePageView.as_view(), name='index'),

    path('list/', views.ListCreateView.as_view(), name='list_create'),
    path('list/<int:pk>/', views.ListDetailView.as_view(), name='list_detail'),
    path('list/<int:pk>/edit/', views.ListUpdateView.as_view(), name='list_update'),
    path('list/<int:pk>/delete/', views.ListDeleteView.as_view(), name='list_delete'),
    path('lists/', views.ListListView.as_view(), name='lists'),

    path('list/<int:list_pk>/task/', views.TaskCreateView.as_view(), name='task_create'),
    path('list/<int:list_pk>/task/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('list/<int:list_pk>/task/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('list/<int:list_pk>/task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('list/<int:list_pk>/tasks/', views.TaskListView.as_view(), name='tasks'),

    # API urls
    path('api/lists/', views.ListListAPIView.as_view(), name='api_lists_list'),
    path('api/lists/<int:pk>/', views.ListDetailAPIView.as_view(), name='api_lists_detail'),
    path('api/lists/<int:list_pk>/tasks/', views.TaskListAPIView.as_view(), name='api_tasks_list'),
    path('api/lists/<int:list_pk>/tasks/<int:pk>/', views.TaskDetailAPIView.as_view(), name='api_tasks_detail'),
    path('api/lists/<int:list_pk>/tasks/<int:pk>/check/', views.TaskCheckApiView.as_view(), name='api_tasks_check'),
    path('api/lists/<int:list_pk>/tasks/<int:pk>/uncheck/', views.TaskUncheckApiView.as_view(), name='api_tasks_uncheck'),
]

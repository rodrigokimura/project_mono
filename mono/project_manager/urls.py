from django.urls import path
from django.views.generic.base import RedirectView
from . import views


app_name = 'project_manager'

urlpatterns = [

    path('', RedirectView.as_view(pattern_name='project_manager:projects'), name='index'),

    path('project/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/', views.ProjectListView.as_view(), name='projects'),

    path('board/', views.BoardCreateView.as_view(), name='board_create'),
    path('board/<int:pk>/', views.BoardDetailView.as_view(), name='board_detail'),
    path('board/<int:pk>/edit/', views.BoardUpdateView.as_view(), name='board_update'),

    # API Routes
    path('api/projects/', views.ProjectListAPIView.as_view()),
    path('api/projects/<int:pk>/', views.ProjectDetailAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/', views.BoardListAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:pk>/', views.BoardDetailAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/', views.BucketListAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:pk>/', views.BucketDetailAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/', views.CardListAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/<int:pk>/', views.CardDetailAPIView.as_view()),
    path('api/card_move/', views.CardMoveApiView.as_view()),
    path('api/bucket_move/', views.BucketMoveApiView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/<int:pk>/timer/', views.StartStopTimerAPIView.as_view()),

]

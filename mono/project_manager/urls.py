"""Project manager's urls"""
from django.urls import path
from django.views.generic.base import RedirectView

from . import views

app_name = 'project_manager'

# pylint: disable=C0301
urlpatterns = [

    path('', RedirectView.as_view(pattern_name='project_manager:projects'), name='index'),

    path('project/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/', views.ProjectListView.as_view(), name='projects'),

    path('project/<int:project_pk>/board/', views.BoardCreateView.as_view(), name='board_create'),
    path('project/<int:project_pk>/board/<int:pk>/', views.BoardDetailView.as_view(), name='board_detail'),
    path('project/<int:project_pk>/board/<int:pk>/edit/', views.BoardUpdateView.as_view(), name='board_update'),
    path('project/<int:project_pk>/board/<int:pk>/calendar/', views.BoardCalendarView.as_view(), name='board_calendar'),

    path('invites/accept/', views.InviteAcceptanceView.as_view(), name='invite_acceptance'),

    # API Routes
    path('api/projects/', views.ProjectListAPIView.as_view()),
    path('api/projects/<int:pk>/', views.ProjectDetailAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/', views.BoardListAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:pk>/', views.BoardDetailAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:pk>/last-updated/', views.BoardLastUpdatedAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:pk>/calendar/', views.BoardCalendarAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/tags/', views.TagListAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/tags/<int:pk>/', views.TagDetailAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/', views.BucketListAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:pk>/', views.BucketDetailAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/', views.CardListAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/<int:pk>/', views.CardDetailAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/<int:card_pk>/files/', views.CardFileListAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/<int:card_pk>/files/<int:pk>/', views.CardFileDetailAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/<int:card_pk>/items/', views.ItemListAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/<int:card_pk>/items/<int:pk>/', views.ItemDetailAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/<int:card_pk>/items/<int:pk>/check/', views.ItemCheckAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/<int:card_pk>/comments/', views.CommentListAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/<int:card_pk>/comments/<int:pk>/', views.CommentDetailAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/<int:card_pk>/time-entries/', views.TimeEntryListAPIView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/<int:card_pk>/time-entries/<int:pk>/', views.TimeEntryDetailAPIView.as_view()),
    path('api/card-move/', views.CardMoveApiView.as_view()),
    path('api/bucket-move/', views.BucketMoveApiView.as_view()),
    path('api/projects/<int:project_pk>/boards/<int:board_pk>/buckets/<int:bucket_pk>/cards/<int:pk>/timer/', views.StartStopTimerAPIView.as_view()),
    path('api/projects/<int:project_pk>/remove-user/', views.ProjectRemoveUserAPIView.as_view()),
    path('api/projects/<int:project_pk>/invites/', views.InviteListAPIView.as_view()),
    path('api/projects/<int:project_pk>/invites/<int:pk>/', views.InviteDetailAPIView.as_view()),
    path('api/projects/<int:project_pk>/invites/<int:pk>/resend/', views.InviteResendAPIView.as_view()),

]

from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path("", views.NoteListView.as_view(), name='note_list'),
    path("create/", views.NoteCreateView.as_view(), name='note_create'),
    path("api/notes/<int:id>/", views.NoteDetailApiView.as_view(), name='api_note_detail'),
]

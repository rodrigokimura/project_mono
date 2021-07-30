from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path("", views.NoteListView.as_view(), name='notes'),
    path("notes/", views.NoteCreateView.as_view(), name='note_create'),
    path("notes/<int:pk>/", views.NoteFormView.as_view(), name='note_edit'),
    path("notes/<int:pk>/delete/", views.NoteDeleteView.as_view(), name='note_delete'),
    path("api/notes/<int:pk>/", views.NoteDetailApiView.as_view(), name='api_note_detail'),
]

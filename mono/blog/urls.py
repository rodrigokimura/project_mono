from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path("post/", views.PostCreateView.as_view(), name='post_create'),
    path("post/<int:pk>/", views.PostUpdateView.as_view(), name='post_update'),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name='post_delete'),
    path("posts/", views.PostListView.as_view(), name='posts'),
]

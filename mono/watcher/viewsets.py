"""Finance's viewsets"""
from __mono.permissions import IsCreator
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from .models import Comment
from .serializers import CommentSerializer

# pylint: disable=too-many-ancestors


class CommentViewSet(ModelViewSet):
    """Comment viewset"""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsCreator, IsAdminUser]
    filterset_fields = {
        'issue__id': ['exact'],
    }

from rest_framework.viewsets import ModelViewSet
from .serializers import UserSerializer, BoardSerializer, ProjectSerializer
from django.contrib.auth.models import User
from .models import Board, Project


class UserViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProjectViewSet(ModelViewSet):

    queryset = Project.objects.order_by('id').all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)


class BoardViewSet(ModelViewSet):

    queryset = Board.objects.order_by('id').all()
    serializer_class = BoardSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)

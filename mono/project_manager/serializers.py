from rest_framework.serializers import HyperlinkedModelSerializer
from django.contrib.auth.models import User
from .models import Project, Board, Bucket, Card


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            'url',
            'username',
            'email',
            'is_staff'
        ]


class ProjectSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = [
            'url',
            'name',
            'created_by',
            'created_at',
            'assigned_to',
        ]


class BoardSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Board
        fields = [
            'url',
            'name',
            'created_by',
            'created_at',
            'project',
            'assigned_to',
        ]


class BucketSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Bucket
        fields = [
            'url',
            'name',
            'created_by',
            'created_at',
            'project',
            'assigned_to',
        ]


class CardSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Card
        fields = [
            'url',
            'name',
            'created_by',
            'created_at',
            'project',
            'assigned_to',
        ]

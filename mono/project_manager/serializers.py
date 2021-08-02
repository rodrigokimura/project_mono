from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import Project, Board, Bucket, Card


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'is_staff'
        ]


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'name',
            'created_by',
            'created_at',
            'assigned_to',
        ]


class BoardSerializer(ModelSerializer):
    class Meta:
        model = Board
        fields = [
            'name',
            'created_by',
            'created_at',
            'project',
            'assigned_to',
        ]


class BucketSerializer(ModelSerializer):
    class Meta:
        model = Bucket
        fields = [
            'id',
            'name',
            'created_by',
            'created_at',
            'board',
            'order',
        ]


class CardSerializer(ModelSerializer):
    class Meta:
        model = Card
        fields = [
            'id',
            'name',
            'bucket',
            'order',
            'assigned_to',
            'description',
            'completed_by',
            'completed_at',
        ]
        extra_kwargs = {'created_by': {'read_only': True}}

from rest_framework.serializers import ModelSerializer
from .models import List, Task


class ListSerializer(ModelSerializer):

    class Meta:
        model = List
        fields = [
            'id',
            'name',
            'created_by',
        ]
        read_only_fields = ['created_by']


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'list',
            'description',
            'order',
            'created_by',
            'created_at',
            'checked_by',
            'checked_at',
        ]
        read_only_fields = ['created_by', 'checked_by', 'checked_at']

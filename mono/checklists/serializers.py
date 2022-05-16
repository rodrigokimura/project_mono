"""Todo lists's serializers"""
from rest_framework import serializers
from rest_framework.serializers import (
    CurrentUserDefault, HiddenField, ModelSerializer, Serializer,
)

from .models import Checklist, Task


class ChecklistSerializer(ModelSerializer):
    """
    Checklist serializer
    """
    created_by = HiddenField(
        default=CurrentUserDefault()
    )

    class Meta:
        model = Checklist
        fields = [
            'id',
            'name',
            'created_by',
        ]
        read_only_fields = ['created_by']


class TaskSerializer(ModelSerializer):
    """
    Task serializer
    """
    created_by = HiddenField(
        default=CurrentUserDefault()
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'checklist',
            'description',
            'note',
            'order',
            'created_by',
            'created_at',
            'checked_by',
            'checked_at',
            'reminder',
            'reminded',
            'due_date',
        ]
        read_only_fields = ['created_by', 'checked_by', 'checked_at']


class ChecklistMoveSerializer(Serializer):
    """Serializer to apply checklist movement"""
    checklist = serializers.IntegerField()
    order = serializers.IntegerField()

    def validate_task(self, value):  # pylint: disable=no-self-use
        """Checklist needs to exist"""
        if Checklist.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Invalid checklist")

    def validate_order(self, value):  # pylint: disable=no-self-use
        """Order needs to be positive"""
        if value > 0:
            return value
        raise serializers.ValidationError("Invalid order")

    def validate(self, attrs):
        """
        Validate user and checklist
        """
        task = Checklist.objects.get(id=attrs['checklist'])

        if task.created_by != self.context['request'].user:
            raise serializers.ValidationError("User not allowed")
        return attrs

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        """
        Apply chacklist movement
        """
        checklist = Checklist.objects.get(
            id=self.validated_data['checklist']
        )
        order = self.validated_data['order']

        for i, other_checklist in enumerate(Checklist.objects.filter(created_by=self.context['request'].user).exclude(id=self.validated_data['checklist'])):
            if i + 1 < order:
                other_checklist.order = i + 1
                other_checklist.save()
            else:
                other_checklist.order = i + 2
                other_checklist.save()
        checklist.order = order
        checklist.save()


class TaskMoveSerializer(Serializer):
    """Serializer to apply task movement"""
    task = serializers.IntegerField()
    order = serializers.IntegerField()

    def validate_task(self, value):  # pylint: disable=no-self-use
        """Task needs to exist"""
        if Task.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Invalid task")

    def validate_order(self, value):  # pylint: disable=no-self-use
        """Order needs to be positive"""
        if value > 0:
            return value
        raise serializers.ValidationError("Invalid order")

    def validate(self, attrs):
        """
        Validate user and task
        """
        task = Task.objects.get(id=attrs['task'])

        if task.created_by != self.context['request'].user:
            raise serializers.ValidationError("User not allowed")
        return attrs

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        """
        Apply task movement
        """
        task = Task.objects.get(
            id=self.validated_data['task']
        )
        order = self.validated_data['order']

        for i, other_task in enumerate(Task.objects.filter(checklist=task.checklist).exclude(id=self.validated_data['task'])):
            if i + 1 < order:
                other_task.order = i + 1
                other_task.save()
            else:
                other_task.order = i + 2
                other_task.save()
        task.order = order
        task.save()

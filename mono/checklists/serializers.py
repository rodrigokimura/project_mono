"""Todo lists's serializers"""
from django.db import transaction
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

    @transaction.atomic
    def create(self, validated_data):
        checklist = super().create(validated_data)
        checklist.order = Checklist.objects.filter(created_by=validated_data['created_by']).count()
        checklist.save()
        return checklist


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

    @transaction.atomic
    def create(self, validated_data):
        task = super().create(validated_data)
        task.order = Task.objects.filter(checklist=task.checklist).count()
        task.save()
        return task


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
        checklist.set_order(order)


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
        task.set_order(order)

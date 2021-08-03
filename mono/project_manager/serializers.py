from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
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
        extra_kwargs = {'created_by': {'read_only': True}}


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
        extra_kwargs = {'created_by': {'read_only': True}}


class BucketSerializer(ModelSerializer):
    class Meta:
        model = Bucket
        fields = [
            'id',
            'name',
            'description',
            'created_by',
            'created_at',
            'board',
            'order',
        ]
        extra_kwargs = {'created_by': {'read_only': True}}


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


class CardMoveSerializer(Serializer):
    source_bucket = serializers.IntegerField()
    target_bucket = serializers.IntegerField()
    order = serializers.IntegerField()
    card = serializers.IntegerField()

    def validate_souce_bucket(self, value):
        if Bucket.objects.filter(id=value).exists():
            return value
        else:
            raise serializers.ValidationError("Invalid bucket")

    def validate_target_bucket(self, value):
        if Bucket.objects.filter(id=value).exists():
            return value
        else:
            raise serializers.ValidationError("Invalid bucket")

    def validate_card(self, value):
        if Card.objects.filter(id=value).exists():
            return value
        else:
            raise serializers.ValidationError("Invalid bucket")

    def validate_order(self, value):
        if value > 0:
            return value
        else:
            raise serializers.ValidationError("Invalid order")

    def validate(self, data):
        source_bucket = Bucket.objects.get(id=data['source_bucket'])
        target_bucket = Bucket.objects.get(id=data['target_bucket'])

        if self.context['request'].user not in source_bucket.board.allowed_users:
            raise serializers.ValidationError("User not allowed")

        if self.context['request'].user not in target_bucket.board.allowed_users:
            raise serializers.ValidationError("User not allowed")

        return data

    def save(self):
        source_bucket = Bucket.objects.get(
            id=self.validated_data['source_bucket']
        )
        target_bucket = Bucket.objects.get(
            id=self.validated_data['target_bucket']
        )
        card = Card.objects.get(
            id=self.validated_data['card']
        )
        order = self.validated_data['order']

        if source_bucket == target_bucket:
            for i, c in enumerate(target_bucket.card_set.exclude(id=self.validated_data['card'])):
                if i + 1 < order:
                    c.order = i + 1
                    c.save()
                else:
                    c.order = i + 2
                    c.save()
            card.order = order
            card.save()
        else:
            for i, c in enumerate(target_bucket.card_set.all()):
                if i + 1 >= order:
                    c.order = i + 2
                    c.save()
            card.bucket = target_bucket
            card.order = order
            card.save()
            for i, c in enumerate(source_bucket.card_set.all()):
                c.order = i + 1
                c.save()

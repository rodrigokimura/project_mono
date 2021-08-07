from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from django.contrib.auth.models import User
from .models import Project, Board, Bucket, Card, Theme, Invite


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'is_staff',
        ]


class ThemeSerializer(ModelSerializer):
    class Meta:
        model = Theme
        fields = [
            'id',
            'name',
            'primary',
            'dark',
            'light',
        ]


class InviteSerializer(ModelSerializer):
    created_by = UserSerializer(many=False, read_only=True)
    accepted_by = UserSerializer(many=False, read_only=True)
    link = serializers.ReadOnlyField()
    class Meta:
        model = Invite
        fields = [
            'email',
            'project',
            'created_by',
            'created_at',
            'accepted_by',
            'accepted_at',
            'link',
        ]
        extra_kwargs = {
            'created_by': {'read_only': True},
            'created_at': {'read_only': True},
            'accepted_by': {'read_only': True},
            'accepted_at': {'read_only': True},
            'link': {'read_only': True},
        }


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
            'created_at',
            'project',
            'assigned_to',
        ]
        extra_kwargs = {'created_by': {'read_only': True}}


class BucketSerializer(ModelSerializer):

    color = ThemeSerializer(many=False, read_only=True)

    class Meta:
        model = Bucket
        fields = [
            'id',
            'name',
            'description',
            'created_at',
            'board',
            'order',
            'auto_status',
            'color',
        ]
        extra_kwargs = {'created_by': {'read_only': True}}


class CardSerializer(ModelSerializer):
    is_running = serializers.ReadOnlyField()
    total_time = serializers.ReadOnlyField()
    color = ThemeSerializer(many=False, read_only=True)

    class Meta:
        model = Card
        fields = [
            'id',
            'name',
            'bucket',
            'order',
            'assigned_to',
            'description',
            'started_by',
            'started_at',
            'completed_by',
            'completed_at',
            'status',
            'is_running',
            'total_time',
            'color',
        ]
        extra_kwargs = {
            'created_by': {'read_only': True},
            'started_by': {'read_only': True},
            'started_at': {'read_only': True},
            'completed_by': {'read_only': True},
            'completed_at': {'read_only': True},
        }

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        status = validated_data.get('status', instance.status)
        if status == Bucket.COMPLETED:
            instance.mark_as_completed(
                user=self.context['request'].user
            )
        elif status == Bucket.IN_PROGRESS:
            instance.mark_as_in_progress(
                user=self.context['request'].user
            )
        elif status == Bucket.NOT_STARTED:
            instance.mark_as_not_started()
        return instance


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

    def move(self):
        status_changed = False
        timer_action = 'none'
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

            # Apply auto_status
            auto_status = target_bucket.auto_status
            if auto_status != Bucket.NONE:
                if auto_status in [Bucket.COMPLETED, Bucket.NOT_STARTED]:
                    timer_action = card.stop_timer().get('action', 'none')
                elif auto_status == Bucket.IN_PROGRESS:
                    timer_action = card.start_timer(self.context['request'].user).get('action', 'none')
                card.status = auto_status
                card.save()
                status_changed = True
        return {
            'success': True,
            'status_changed': status_changed,
            'timer_action': timer_action,
        }


class BucketMoveSerializer(Serializer):
    board = serializers.IntegerField()
    bucket = serializers.IntegerField()
    order = serializers.IntegerField()

    def validate_board(self, value):
        if Board.objects.filter(id=value).exists():
            return value
        else:
            raise serializers.ValidationError("Invalid board")

    def validate_bucket(self, value):
        if Bucket.objects.filter(id=value).exists():
            return value
        else:
            raise serializers.ValidationError("Invalid bucket")

    def validate_order(self, value):
        if value > 0:
            return value
        else:
            raise serializers.ValidationError("Invalid order")

    def validate(self, data):
        bucket = Bucket.objects.get(id=data['bucket'])
        board = Board.objects.get(id=data['board'])

        if self.context['request'].user not in board.allowed_users:
            raise serializers.ValidationError("User not allowed")

        if bucket not in board.bucket_set.all():
            raise serializers.ValidationError("Bucket outside board")

        return data

    def save(self):
        bucket = Bucket.objects.get(
            id=self.validated_data['bucket']
        )
        board = Board.objects.get(
            id=self.validated_data['board']
        )
        order = self.validated_data['order']

        for i, b in enumerate(board.bucket_set.exclude(id=self.validated_data['bucket'])):
            if i + 1 < order:
                b.order = i + 1
                b.save()
            else:
                b.order = i + 2
                b.save()
        bucket.order = order
        bucket.save()

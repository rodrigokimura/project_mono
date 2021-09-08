from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from django.contrib.auth.models import User
from accounts.models import UserProfile
import json
from .models import Comment, Icon, Item, Project, Board, Bucket, Card, Tag, Theme, Invite, TimeEntry


class ProfileSerializer(ModelSerializer):

    class Meta:
        model = UserProfile
        fields = [
            'avatar'
        ]


class UserSerializer(ModelSerializer):
    profile = ProfileSerializer(many=False, read_only=True)

    class Meta:
        model = User

        fields = [
            'username',
            'email',
            'profile',
        ]
        extra_kwargs = {
            'username': {'read_only': True},
            'email': {'read_only': True},
            'profile': {'read_only': True},
        }


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
            'project': {'required': True},
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
    allowed_users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            'name',
            'created_at',
            'project',
            'assigned_to',
            'fullscreen',
            'compact',
            'dark',
            'bucket_width',
            'allowed_users',
            'background_image',
        ]
        extra_kwargs = {'created_by': {'read_only': True}}

    def update(self, instance, validated_data):
        if validated_data['background_image'] is None:
            instance.background_image = None
        return super().update(instance, validated_data)


class BucketSerializer(ModelSerializer):

    color = ThemeSerializer(many=False, read_only=True)

    class Meta:
        model = Bucket
        fields = [
            'id',
            'name',
            'description',
            'created_at',
            'updated_at',
            'board',
            'order',
            'auto_status',
            'color',
        ]
        extra_kwargs = {'created_by': {'read_only': True}}

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.board.touch()
        return instance

    def update(self, instance, validated_data):
        instance.board.touch()
        return super().update(instance, validated_data)


class IconSerializer(ModelSerializer):
    class Meta:
        model = Icon
        fields = [
            'id',
            'markup',
        ]


class TagSerializer(ModelSerializer):

    icon = IconSerializer(many=False, read_only=True, required=False)
    color = ThemeSerializer(many=False, read_only=True, required=False)

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'icon',
            'color',
        ]

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.board.touch()

    def update(self, instance, validated_data):
        if 'icon' in validated_data:
            del validated_data['icon']
        icon_id = self.context['request'].data.get('icon')
        if icon_id not in ['', None]:
            icon = Icon.objects.get(id=int(icon_id))
            instance.icon = icon
        else:
            instance.icon = None
        theme_id = self.context['request'].data.get('color')
        if theme_id not in ['', None]:
            theme = Theme.objects.get(id=int(theme_id))
            instance.color = theme
        else:
            instance.color = None
        super().update(instance, validated_data)
        instance.save()
        instance.board.touch()

        return instance


class CardSerializer(ModelSerializer):
    allowed_users = UserSerializer(many=True, read_only=True)
    is_running = serializers.ReadOnlyField()
    total_time = serializers.ReadOnlyField()
    checked_items = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()
    comments = serializers.ReadOnlyField()
    color = ThemeSerializer(many=False, read_only=True)
    tag = TagSerializer(many=True, required=False)
    assigned_to = UserSerializer(many=True, required=False)

    class Meta:
        model = Card
        fields = [
            'id',
            'tag',
            'name',
            'bucket',
            'order',
            'assigned_to',
            'description',
            'due_date',
            'started_by',
            'started_at',
            'completed_by',
            'completed_at',
            'status',
            'allowed_users',
            'is_running',
            'total_time',
            'checked_items',
            'total_items',
            'comments',
            'color',
        ]
        extra_kwargs = {
            'created_by': {'read_only': True},
            'started_by': {'read_only': True},
            'started_at': {'read_only': True},
            'completed_by': {'read_only': True},
            'completed_at': {'read_only': True},
        }

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.bucket.touch()
        if 'tag' in validated_data:
            del validated_data['tag']

        requested_tags = self.context['request'].data.get('tag')
        if requested_tags is not None:
            requested_tags = json.loads(requested_tags)
        else:
            requested_tags = []

        tags = []
        for tag_dict in requested_tags:
            if tag_dict['name'].strip() == '':
                continue
            tag, created = Tag.objects.update_or_create(
                name=tag_dict['name'],
                defaults={
                    'created_by': self.context['request'].user,
                    'board': validated_data['bucket'].board,
                }
            )
            tags.append(tag)

        requested_assignees = self.context['request'].data.get('assigned_to')
        if requested_assignees is not None:
            requested_assignees = json.loads(requested_assignees)
        else:
            requested_assignees = []

        assignees = []
        for user_dict in requested_assignees:
            qs = User.objects.filter(username=user_dict.get('username', ''))
            if qs.exists():
                user = qs.get()
                if user in instance.allowed_users:
                    assignees.append(user)

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
        instance.tag.set(tags)
        instance.assigned_to.set(assignees)
        return instance

    def update(self, instance, validated_data):
        instance.bucket.touch()
        if 'tag' in validated_data:
            del validated_data['tag']

        requested_tags = self.context['request'].data.get('tag')
        if requested_tags is not None:
            requested_tags = json.loads(requested_tags)

        tags = []
        if requested_tags is not None:
            for tag_dict in requested_tags:
                if tag_dict['name'].strip() == '':
                    continue
                tag, created = Tag.objects.update_or_create(
                    name=tag_dict['name'],
                    defaults={
                        'created_by': self.context['request'].user,
                        'board': validated_data['bucket'].board,
                    }
                )
                tags.append(tag)

        requested_assignees = self.context['request'].data.get('assigned_to')
        if requested_assignees is not None:
            requested_assignees = json.loads(requested_assignees)

        assignees = []
        if requested_assignees is not None:
            for user_dict in requested_assignees:
                qs = User.objects.filter(username=user_dict.get('username', ''))
                if qs.exists():
                    user = qs.get()
                    if user in instance.allowed_users:
                        assignees.append(user)

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
        if requested_tags is not None:
            instance.tag.set(tags)
        if requested_assignees is not None:
            instance.assigned_to.set(assignees)
        return instance


class ItemSerializer(ModelSerializer):
    checked = serializers.ReadOnlyField()

    class Meta:
        model = Item
        fields = [
            'id',
            'name',
            'card',
            'order',
            'checked_by',
            'checked_at',
            'checked',
        ]
        extra_kwargs = {
            'created_by': {'read_only': True},
            'checked_by': {'read_only': True},
            'checked_at': {'read_only': True},
            'checked': {'read_only': True},
        }

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.card.bucket.touch()
        return instance


class TimeEntrySerializer(ModelSerializer):

    class Meta:
        model = TimeEntry
        fields = [
            'id',
            'name',
            'card',
            'started_at',
            'stopped_at',
        ]
        extra_kwargs = {
            'created_by': {'read_only': True},
        }

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.card.bucket.touch()
        return instance

    def update(self, instance, validated_data):
        instance.card.bucket.touch()
        return super().update(instance, validated_data)


class CommentSerializer(ModelSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'text',
            'card',
            'created_by',
            'created_at',
        ]
        extra_kwargs = {
            'created_by': {'read_only': True},
            'created_at': {'read_only': True},
        }

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.card.bucket.touch()
        return instance


class CardMoveSerializer(Serializer):
    source_bucket = serializers.IntegerField()
    target_bucket = serializers.IntegerField()
    order = serializers.IntegerField()
    card = serializers.IntegerField()

    def validate_source_bucket(self, value):
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
            raise serializers.ValidationError("Invalid card")

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
        source_bucket.touch()
        target_bucket.touch()
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
        bucket.board.touch()

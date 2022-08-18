"""Project manager's serializers"""
import json
import os

from __mono.utils import validate_file_size
from accounts.serializers import ProfileSerializer
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import (
    CurrentUserDefault,
    HiddenField,
    ModelSerializer,
    Serializer,
)

from .models import (
    Activity,
    Board,
    Bucket,
    Card,
    CardFile,
    Comment,
    Configuration,
    Icon,
    Invite,
    Item,
    Project,
    Space,
    Tag,
    Theme,
    TimeEntry,
    User,
)


def _delete_file(path):
    """Deletes file from filesystem."""
    if os.path.isfile(path):
        os.remove(path)


class UserSerializer(ModelSerializer):
    """User serializer"""

    profile = ProfileSerializer(many=False, read_only=True)
    has_timer_running = serializers.BooleanField(required=False)

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "profile",
            "has_timer_running",
        ]
        extra_kwargs = {
            "username": {"read_only": True},
            "email": {"read_only": True},
            "profile": {"read_only": True},
        }


class ThemeSerializer(ModelSerializer):
    """Serializer for theme"""

    class Meta:
        model = Theme
        fields = [
            "id",
            "name",
            "primary",
            "dark",
            "light",
        ]


class InviteSerializer(ModelSerializer):
    """Serializer for invite"""

    created_by = UserSerializer(many=False, read_only=True)
    accepted_by = UserSerializer(many=False, read_only=True)
    link = serializers.ReadOnlyField()

    class Meta:
        model = Invite
        fields = [
            "id",
            "email",
            "project",
            "created_by",
            "created_at",
            "accepted_by",
            "accepted_at",
            "link",
        ]
        extra_kwargs = {
            "email": {"required": False},
            "project": {"required": True},
            "id": {"read_only": True},
            "created_by": {"read_only": True},
            "created_at": {"read_only": True},
            "accepted_by": {"read_only": True},
            "accepted_at": {"read_only": True},
            "link": {"read_only": True},
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=("email", "project"),
                message=_(
                    "You've already invited this email for this project."
                ),
            )
        ]


class ProjectSerializer(ModelSerializer):
    """Serializer for project"""

    class Meta:
        model = Project
        fields = [
            "name",
            "created_by",
            "created_at",
            "assigned_to",
        ]
        extra_kwargs = {"created_by": {"read_only": True}}


class BoardSerializer(ModelSerializer):
    """Serializer for board"""

    allowed_users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "name",
            "created_at",
            "project",
            "assigned_to",
            "allowed_users",
            "background_image",
            "card_count",
            "progress",
            "space",
        ]
        extra_kwargs = {
            "created_by": {"read_only": True},
            "card_count": {"read_only": True},
            "progress": {"read_only": True},
        }

    def update(self, instance, validated_data):
        """Handle background image deletion upon update"""
        if "background_image" in validated_data:
            if instance.background_image:
                _delete_file(instance.background_image.path)
            if validated_data["background_image"] is None:
                instance.background_image = None
        return super().update(instance, validated_data)


class BucketSerializer(ModelSerializer):
    """Serializer for bucket"""

    color = ThemeSerializer(many=False, read_only=True)

    class Meta:
        model = Bucket
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "board",
            "order",
            "auto_status",
            "color",
        ]
        extra_kwargs = {"created_by": {"read_only": True}}

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.board.touch()
        return instance

    def update(self, instance, validated_data):
        instance.board.touch()
        return super().update(instance, validated_data)


class IconSerializer(ModelSerializer):
    """Serializer for icon"""

    class Meta:
        model = Icon
        fields = [
            "id",
            "markup",
        ]


class TagSerializer(ModelSerializer):
    """Serializer for tag"""

    icon = IconSerializer(many=False, read_only=True, required=False)
    color = ThemeSerializer(many=False, read_only=True, required=False)

    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
            "icon",
            "color",
        ]

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.board.touch()
        return instance

    def update(self, instance, validated_data):
        """Handle icon and color"""
        if "icon" in validated_data:
            del validated_data["icon"]
        icon_id = self.context["request"].data.get("icon")
        if icon_id not in ["", None]:
            icon = Icon.objects.get(id=int(icon_id))
            instance.icon = icon
        else:
            instance.icon = None
        theme_id = self.context["request"].data.get("color")
        if theme_id not in ["", None]:
            theme = Theme.objects.get(id=int(theme_id))
            instance.color = theme
        else:
            instance.color = None
        super().update(instance, validated_data)
        instance.save()
        instance.board.touch()

        return instance


class CardFileSerializer(ModelSerializer):
    """Serializer for card file"""

    name = serializers.ReadOnlyField()
    image = serializers.ReadOnlyField()
    extension = serializers.ReadOnlyField()

    class Meta:
        model = CardFile
        fields = [
            "id",
            "file",
            "name",
            "image",
            "extension",
        ]

    def validate_file(self, file):  # pylint: disable=no-self-use
        return validate_file_size(file, 10)

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.card.bucket.touch()
        return instance


class ActivitySerializer(ModelSerializer):
    """Serializer for card activities"""

    verbose_text = serializers.ReadOnlyField()
    detailed_text = serializers.ReadOnlyField()

    class Meta:
        model = Activity
        fields = [
            "verbose_text",
            "detailed_text",
        ]


class CardSerializer(ModelSerializer):
    """Serializer for card"""

    is_running = serializers.ReadOnlyField()
    total_time = serializers.ReadOnlyField()
    checked_items = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()
    total_files = serializers.ReadOnlyField()
    comments = serializers.ReadOnlyField()
    color = ThemeSerializer(many=False, read_only=True)
    tag = TagSerializer(many=True, required=False)
    assigned_to = UserSerializer(many=True, required=False)
    files = CardFileSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = [
            "id",
            "tag",
            "name",
            "bucket",
            "order",
            "assigned_to",
            "description",
            "due_date",
            "status",
            "is_running",
            "total_time",
            "checked_items",
            "total_items",
            "total_files",
            "comments",
            "color",
            "files",
        ]
        extra_kwargs = {
            "created_by": {"read_only": True},
            "started_by": {"read_only": True},
            "started_at": {"read_only": True},
            "completed_by": {"read_only": True},
            "completed_at": {"read_only": True},
        }

    def _create_tags(self, requested_tags, card):
        """Create tags from data"""
        tags = []
        if requested_tags is None:
            return tags
        for tag_dict in requested_tags:
            if tag_dict["name"].strip() == "":
                continue
            tag, _ = Tag.objects.update_or_create(
                name=tag_dict["name"],
                board=card.bucket.board,
                defaults={
                    "created_by": self.context["request"].user,
                    "board": card.bucket.board,
                },
            )
            tags.append(tag)
        return tags

    def _apply_status(self, card: Card, status: str):
        """Apply status to card"""
        if status == Bucket.COMPLETED:
            card.mark_as_completed(user=self.context["request"].user)
        elif status == Bucket.IN_PROGRESS:
            card.mark_as_in_progress(user=self.context["request"].user)
        elif status == Bucket.NOT_STARTED:
            card.mark_as_not_started()

    def create(self, validated_data):
        """Process creation"""
        instance = super().create(validated_data)
        instance.bucket.touch()
        if "tag" in validated_data:
            del validated_data["tag"]

        requested_tags = self.context["request"].data.get("tag")
        if requested_tags is not None:
            requested_tags = json.loads(requested_tags)
        else:
            requested_tags = []

        tags = self._create_tags(requested_tags, instance)

        requested_assignees = self.context["request"].data.get("assigned_to")
        if requested_assignees is not None:
            requested_assignees = json.loads(requested_assignees)
        else:
            requested_assignees = []

        assignees = []
        for user_dict in requested_assignees:
            qs = User.objects.filter(username=user_dict.get("username", ""))
            if qs.exists():
                user = qs.get()
                if user in instance.allowed_users:
                    assignees.append(user)

        status = validated_data.get("status", instance.status)
        self._apply_status(instance, status)
        instance.tag.set(tags)
        instance.assigned_to.set(assignees)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        """Process update"""
        instance.bucket.touch()
        if "tag" in validated_data:
            del validated_data["tag"]

        requested_tags = self.context["request"].data.get("tag")
        if requested_tags is not None:
            requested_tags = json.loads(requested_tags)
        tags = self._create_tags(requested_tags, instance)

        requested_assignees = self.context["request"].data.get("assigned_to")
        if requested_assignees is not None:
            requested_assignees = json.loads(requested_assignees)

        assignees = []
        if requested_assignees is not None:
            for user_dict in requested_assignees:
                qs = User.objects.filter(username=user_dict.get("username", ""))
                if qs.exists():
                    user = qs.get()
                    if user in instance.allowed_users:
                        assignees.append(user)

        super().update(instance, validated_data)
        status = validated_data.get("status", instance.status)
        self._apply_status(instance, status)

        if requested_tags is not None:
            Activity.create_activity_for_tags(
                instance,
                self.context["request"].user,
                set(instance.tag.all()),
                set(tags),
            )
            instance.tag.set(tags)
        if requested_assignees is not None:
            Activity.create_activity_for_assigned_users(
                instance,
                self.context["request"].user,
                set(instance.assigned_to.all()),
                set(assignees),
            )
            instance.assigned_to.set(assignees)
        return instance


class ItemSerializer(ModelSerializer):
    """Serializer for item"""

    checked = serializers.ReadOnlyField()

    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "card",
            "order",
            "checked_by",
            "checked_at",
            "checked",
        ]
        extra_kwargs = {
            "created_by": {"read_only": True},
            "checked_by": {"read_only": True},
            "checked_at": {"read_only": True},
            "checked": {"read_only": True},
        }

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.card.bucket.touch()
        return instance


class TimeEntrySerializer(ModelSerializer):
    """Serializer for time entry"""

    class Meta:
        model = TimeEntry
        fields = [
            "id",
            "name",
            "card",
            "started_at",
            "stopped_at",
        ]
        extra_kwargs = {
            "created_by": {"read_only": True},
        }

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.card.bucket.touch()
        return instance

    def update(self, instance, validated_data):
        instance.card.bucket.touch()
        return super().update(instance, validated_data)


class CommentSerializer(ModelSerializer):
    """Serializer for comment"""

    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "text",
            "card",
            "created_by",
            "created_at",
        ]
        extra_kwargs = {
            "created_by": {"read_only": True},
            "created_at": {"read_only": True},
        }

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.card.bucket.touch()
        return instance


class CardMoveSerializer(Serializer):
    """Serializer to apply card movement"""

    source_bucket = serializers.IntegerField()
    target_bucket = serializers.IntegerField()
    order = serializers.IntegerField()
    card = serializers.IntegerField()

    def validate_source_bucket(self, value):  # pylint: disable=no-self-use
        """Bucket needs to exist"""
        if Bucket.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Invalid bucket")

    def validate_target_bucket(self, value):  # pylint: disable=no-self-use
        """Bucket needs to exist"""
        if Bucket.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Invalid bucket")

    def validate_card(self, value):  # pylint: disable=no-self-use
        """Card needs to exist"""
        if Card.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Invalid card")

    def validate_order(self, value):  # pylint: disable=no-self-use
        """Order has to be positive"""
        if value > 0:
            return value
        raise serializers.ValidationError("Invalid order")

    def validate(self, attrs):
        """Validate buckets and user"""
        source_bucket = Bucket.objects.get(id=attrs["source_bucket"])
        target_bucket = Bucket.objects.get(id=attrs["target_bucket"])

        if (
            self.context["request"].user
            not in source_bucket.board.allowed_users
        ):
            raise serializers.ValidationError("User not allowed")

        if (
            self.context["request"].user
            not in target_bucket.board.allowed_users
        ):
            raise serializers.ValidationError("User not allowed")

        return attrs

    def move(self):
        """Apply movement"""
        status_changed = False
        timer_action = "none"
        source_bucket = Bucket.objects.get(
            id=self.validated_data["source_bucket"]
        )
        target_bucket = Bucket.objects.get(
            id=self.validated_data["target_bucket"]
        )
        card: Card = Card.objects.get(id=self.validated_data["card"])
        order = self.validated_data["order"]
        card.set_order(target_bucket, order)

        if source_bucket != target_bucket:
            # Apply auto_status
            auto_status = target_bucket.auto_status
            if auto_status != Bucket.NONE:
                if auto_status in [Bucket.COMPLETED, Bucket.NOT_STARTED]:
                    timer_action = card.stop_timer(
                        self.context["request"].user
                    ).get("action", Card.TimerActions.NONE)
                elif auto_status == Bucket.IN_PROGRESS:
                    timer_action = card.start_timer(
                        self.context["request"].user
                    ).get("action", Card.TimerActions.NONE)
                card.status = auto_status
                card.save()
                status_changed = True
        return {
            "success": True,
            "status_changed": status_changed,
            "timer_action": timer_action,
        }

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class BucketMoveSerializer(Serializer):
    """Serializer to apply bucket movement"""

    board = serializers.IntegerField()
    bucket = serializers.IntegerField()
    order = serializers.IntegerField()

    def validate_board(self, value):  # pylint: disable=no-self-use
        """Board needs to exist"""
        if Board.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Invalid board")

    def validate_bucket(self, value):  # pylint: disable=no-self-use
        """Buckes need to exist"""
        if Bucket.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Invalid bucket")

    def validate_order(self, value):  # pylint: disable=no-self-use
        """Order needs to be positive"""
        if value > 0:
            return value
        raise serializers.ValidationError("Invalid order")

    def validate(self, attrs):
        """
        Validate user and board
        """
        bucket = Bucket.objects.get(id=attrs["bucket"])
        board = Board.objects.get(id=attrs["board"])

        if self.context["request"].user not in board.allowed_users:
            raise serializers.ValidationError("User not allowed")

        if bucket not in board.bucket_set.all():
            raise serializers.ValidationError("Bucket outside board")

        return attrs

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        """
        Apply bucket movement
        """
        bucket = Bucket.objects.get(id=self.validated_data["bucket"])
        order = self.validated_data["order"]
        bucket.set_order(order)


class BoardMoveSerializer(Serializer):
    """Serializer to apply board movement"""

    project = serializers.IntegerField()
    board = serializers.IntegerField()
    order = serializers.IntegerField()
    space = serializers.IntegerField(required=False)

    def validate_space(self, value):  # pylint: disable=no-self-use
        """Space needs to exist"""
        if Space.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Invalid space")

    def validate_project(self, value):  # pylint: disable=no-self-use
        """Project needs to exist"""
        if Project.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Invalid project")

    def validate_board(self, value):  # pylint: disable=no-self-use
        """Board needs to exist"""
        if Board.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Invalid board")

    def validate_order(self, value):  # pylint: disable=no-self-use
        """Order needs to be positive"""
        if value > 0:
            return value
        raise serializers.ValidationError("Invalid order")

    def validate(self, attrs):
        """
        Validate user and board
        """
        board = Board.objects.get(id=attrs["board"])
        project = Project.objects.get(id=attrs["project"])

        if self.context["request"].user not in project.allowed_users:
            raise serializers.ValidationError("User not allowed")

        if board not in project.board_set.all():
            raise serializers.ValidationError("Board outside project")

        return attrs

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        """
        Apply board movement
        """
        board: Board = Board.objects.get(id=self.validated_data["board"])
        order = self.validated_data["order"]
        space = Space.objects.filter(
            id=self.validated_data.get("space")
        ).first()
        board.set_order_and_space(order, space)


class SpaceSerializer(ModelSerializer):
    """
    Task serializer
    """

    created_by = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Space
        fields = [
            "id",
            "name",
            "project",
            "order",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at", "project"]

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.project = validated_data["project"]
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.project = validated_data["project"]
        return instance


class ConfigurationSerializer(ModelSerializer):
    """
    Configuration serializer
    """

    user = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Configuration
        fields = [
            "user",
            "created_at",
            "updated_at",
            "compact",
            "dark",
            "bucket_width",
        ]
        read_only_fields = [
            "user",
            "created_at",
            "updated_at",
        ]

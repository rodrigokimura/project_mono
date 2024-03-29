"""Project manager's models"""
import imghdr
import os
import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional

from accounts.models import Notification
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.humanize.templatetags.humanize import NaturalTimeFormatter
from django.core.mail import EmailMultiAlternatives
from django.core.signing import TimestampSigner
from django.db import models, transaction
from django.db.models import (
    DurationField,
    Exists,
    OuterRef,
    Q,
    QuerySet,
    Sum,
    Value as V,
)
from django.db.models.aggregates import Count, Max
from django.db.models.fields import IntegerField
from django.db.models.functions import Coalesce
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

from .icons import DEFAULT_ICONS

User = get_user_model()


class BaseModel(models.Model):
    """
    Base model for this app
    """

    name = models.CharField(max_length=50, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = True


class Project(BaseModel):
    """
    Project that holds boards
    """

    deadline = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ManyToManyField(
        User, related_name="assigned_projects", blank=True
    )
    order = models.IntegerField(default=1)

    class Meta:
        ordering = [
            "created_at",
        ]

    @property
    def allowed_users(self) -> QuerySet[User]:
        return (
            User.objects.filter(id=self.created_by.id) | self.assigned_to.all()
        ).distinct()

    @property
    def card_count(self):
        return Card.objects.filter(bucket__board__project=self).count()

    @property
    def progress(self):
        """
        Display detailed information about project's progress
        """
        qs = Card.objects.filter(bucket__board__project=self.id)
        total_cards = qs.count()
        not_started = qs.filter(status="NS").aggregate(count=Count("id"))[
            "count"
        ]
        in_progress = qs.filter(status="IP").aggregate(count=Count("id"))[
            "count"
        ]
        completed = qs.filter(status="C").aggregate(count=Count("id"))["count"]
        if total_cards == 0:
            completed_perc = 0
            in_progress_perc = 0
            not_started_perc = 0
        else:
            completed_perc = round(completed / total_cards * 100)
            in_progress_perc = round(in_progress / total_cards * 100)
            not_started_perc = 100 - completed_perc - in_progress_perc

        return {
            "completed": [completed, completed_perc],
            "in_progress": [in_progress, in_progress_perc],
            "not_started": [not_started, not_started_perc],
        }

    @property
    def share_link(self):
        """
        Display link to share
        """
        invite: Invite = Invite.objects.get_or_create(
            project=self,
            email__isnull=True,
            accepted_by__isnull=True,
        )[0]
        return invite.link

    def touch(self):
        self.save()

    def sort(self):
        """Fix board order"""
        for index, board in enumerate(self.board_set.all()):
            board.order = index + 1
            board.save()


class Space(BaseModel):
    order = models.PositiveIntegerField()
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="spaces"
    )


class Board(BaseModel):
    """
    Board that holds buckets
    """

    def _background_image_path(self, filename):
        return f"project_{self.project.id}/board_{self.id}/{filename}"

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(
        User, related_name="assigned_boards", blank=True
    )
    order = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    background_image = models.ImageField(
        upload_to=_background_image_path, blank=True, null=True
    )
    space = models.ForeignKey(
        "Space", on_delete=models.SET_NULL, null=True, blank=True, default=None
    )

    tags_feature = models.BooleanField(
        default=True, help_text="Enables tags on cards"
    )
    color_feature = models.BooleanField(
        default=True, help_text="Enables color on cards"
    )
    due_date_feature = models.BooleanField(
        default=True, help_text="Enables cards to have due dates"
    )
    status_feature = models.BooleanField(
        default=True, help_text="Enables status on cards"
    )
    assignees_feature = models.BooleanField(
        default=True, help_text="Enables assignees on cards"
    )
    checklist_feature = models.BooleanField(
        default=True, help_text="Enables checklist on cards"
    )
    files_feature = models.BooleanField(
        default=True, help_text="Enables file attachments on cards"
    )
    comments_feature = models.BooleanField(
        default=True, help_text="Enables users to comment on cards"
    )
    time_entries_feature = models.BooleanField(
        default=True, help_text="Enables users to track time spent on cards"
    )

    @property
    def allowed_users(self):
        return (
            User.objects.filter(
                Q(id=self.created_by.id)
                | Q(id__in=self.assigned_to.all().values_list("id", flat=True))
            )
            .annotate(
                has_timer_running=Exists(
                    TimeEntry.objects.filter(
                        card__bucket__board=self,
                        stopped_at__isnull=True,
                        created_by_id=OuterRef("id"),
                    )
                )
            )
            .distinct()
        )

    @property
    def max_order(self):
        return self.bucket_set.all().aggregate(
            max_order=Coalesce(Max("order"), V(0), output_field=IntegerField())
        )["max_order"]

    def touch(self):
        self.save()

    class Meta:
        ordering = [
            "project",
            "order",
            "created_at",
        ]

    @property
    def card_count(self):
        return Card.objects.filter(bucket__board=self).count()

    @property
    def progress(self):
        """Display detailed information about board's progress"""
        qs = Card.objects.filter(bucket__board=self.id)
        total_cards = qs.count()
        not_started = qs.filter(status="NS").aggregate(count=Count("id"))[
            "count"
        ]
        in_progress = qs.filter(status="IP").aggregate(count=Count("id"))[
            "count"
        ]
        completed = qs.filter(status="C").aggregate(count=Count("id"))["count"]
        if total_cards == 0:
            completed_perc = 0
            in_progress_perc = 0
            not_started_perc = 0
        else:
            completed_perc = round(completed / total_cards * 100)
            in_progress_perc = round(in_progress / total_cards * 100)
            not_started_perc = 100 - completed_perc - in_progress_perc

        return {
            "completed": [completed, completed_perc],
            "in_progress": [in_progress, in_progress_perc],
            "not_started": [not_started, not_started_perc],
        }

    # @transaction.atomic
    def set_order_and_space(
        self, order: int, space: Optional[Space] = None
    ) -> None:
        """
        Set board order and/or move it to a space
        """
        original_space = self.space
        target_space = space
        spaces = [original_space, target_space]

        for _space in spaces:
            boards = Board.objects.filter(
                project=self.project, space=_space
            ).exclude(id=self.id)
            for i, board in enumerate(boards):
                if i + 1 < order:
                    board.order = i + 1
                    board.save()
                else:
                    board.order = i + 2
                    board.save()
        self.order = order
        self.space = space
        self.save()
        self.project.touch()


class Configuration(models.Model):
    """
    User configuration
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="project_manager_config"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    compact = models.BooleanField(default=False)
    dark = models.BooleanField(default=False)
    bucket_width = models.IntegerField(default=300)

    class Meta:
        verbose_name = _("configuration")
        verbose_name_plural = _("configurations")

    def as_dict(self):
        return {
            "compact": self.compact,
            "dark": self.dark,
            "bucket_width": self.bucket_width,
        }


class Bucket(BaseModel):
    """
    Bucket that holds cards
    """

    NONE = "N"
    NOT_STARTED = "NS"
    IN_PROGRESS = "IP"
    COMPLETED = "C"
    STATUSES = [
        (NONE, _("No automatic status")),
        (NOT_STARTED, _("Not started")),
        (IN_PROGRESS, _("In progress")),
        (COMPLETED, _("Completed")),
    ]
    DEFAULT_BUCKETS = [
        (_("To do"), _("Stuff to do"), 1, NOT_STARTED),
        (_("Doing"), _("Stuff being done"), 2, IN_PROGRESS),
        (_("Done"), _("Stuff already finished"), 3, COMPLETED),
    ]
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    order = models.IntegerField()
    description = models.TextField(max_length=255, blank=True, null=True)
    auto_status = models.CharField(
        _("status"), max_length=2, choices=STATUSES, default=NONE
    )
    color = models.ForeignKey(
        "Theme", on_delete=models.CASCADE, blank=True, null=True, default=None
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "board__project",
            "board",
            "order",
        ]

    @transaction.atomic
    def set_order(self, order):
        """
        Set bucket order
        """
        buckets = Bucket.objects.filter(board=self.board).exclude(id=self.id)
        for i, bucket in enumerate(buckets):
            if i + 1 < order:
                bucket.order = i + 1
                bucket.save()
            else:
                bucket.order = i + 2
                bucket.save()
        self.order = order
        self.save()
        self.board.touch()

    @property
    def max_order(self):
        return self.card_set.all().aggregate(
            max_order=Coalesce(Max("order"), V(0), output_field=IntegerField())
        )["max_order"]

    def touch(self):
        self.save()

    @transaction.atomic
    def sort(self):
        """Fix card order"""
        for index, card in enumerate(self.card_set.all()):
            card.order = index + 1
            card.save()


class Tag(BaseModel):
    """
    Tag for generic information and filtering
    """

    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    icon = models.ForeignKey(
        "Icon", on_delete=models.SET_NULL, default=None, null=True, blank=True
    )
    color = models.ForeignKey(
        "Theme", on_delete=models.SET_NULL, default=None, null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["board", "name"], name="unique_tag"
            ),
        ]


class Activity(models.Model):
    """
    Store actions executed for a card to be displayed as history timeline.
    """

    class Action(models.TextChoices):
        """
        Actions to be logged
        """

        CREATE_CARD = "create_card", _("%(user)s created card")
        UPDATE_NAME = "update_name", _(
            "%(user)s updated card name from %(old)s to %(new)s"
        )
        UPDATE_DESCRIPTION = "update_description", _(
            "%(user)s updated card description"
        )
        UPDATE_DUE_DATE = "update_due_date", _(
            "%(user)s updated card due date from %(old)s to %(new)s"
        )
        UPDATE_STATUS = "update_status", _(
            "%(user)s updated card status from %(old)s to %(new)s"
        )
        UPDATE_COLOR = "update_color", _(
            "%(user)s updated card color from %(old)s to %(new)s"
        )
        ADD_TAG = "add_tags", _("%(user)s added tag %(tag)s")
        REMOVE_TAG = "remove_tags", _("%(user)s removed tag %(tag)s")
        ADD_ASSIGNED_USER = "add_assigned_user", _(
            "%(user)s assigned %(assignee)s to card"
        )
        REMOVE_ASSIGNED_USER = "remove_assigned_user", _(
            "%(user)s removed %(assignee)s from card's assigned users"
        )
        ADD_CHECKLIST_ITEM = "add_checklist_item", _(
            "%(user)s added checklist item %(item)s"
        )
        UPDATE_CHECKLIST_ITEM = "update_checklist_item", _(
            "%(user)s updated checklist item from %(old)s to %(new)s"
        )
        REMOVE_CHECKLIST_ITEM = "remove_checklist_item", _(
            "%(user)s removed checklist item %(item)s"
        )
        ADD_COMMENT = "add_comment", _("%(user)s added comment")
        UPDATE_COMMENT = "update_comment", _("%(user)s updated comment")
        REMOVE_COMMENT = "remove_comment", _("%(user)s removed comment")
        ADD_FILE = "add_file", _("%(user)s added a file")
        REMOVE_FILE = "remove_file", _("%(user)s removed a file")
        START_TIMER = "start_timer", _("%(user)s started timer")
        STOP_TIMER = "stop_timer", _(
            "%(user)s stopped timer (logged duration: %(duration)s)"
        )
        UPDATE_TIME_ENTRY = (
            "update_time_entry",
            _(
                "%(user)s updated a time entry (duration changed from %(old)s to %(new)s)"
            ),
        )
        DELETE_TIME_ENTRY = "delete_time_entry", _(
            "%(user)s deleted a time entry"
        )

    card = models.ForeignKey(
        "Card", on_delete=models.CASCADE, related_name="activities"
    )
    action = models.CharField(
        max_length=100, null=False, blank=False, choices=Action.choices
    )
    context = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("activity")
        verbose_name_plural = _("activities")

    def __str__(self) -> str:
        return self.action

    @classmethod
    @transaction.atomic
    def create_activities_for_fields(
        cls, card, user, data: Optional[Dict[str, Any]] = None
    ):
        """
        Method to create activities when a card attribute is changed.
        """
        if data is None:
            cls.objects.create(
                action=cls.Action.CREATE_CARD,
                created_by=user,
                card=card,
            )
            return
        field_action_mapping = {
            "name": cls.Action.UPDATE_NAME.value,
            "description": cls.Action.UPDATE_DESCRIPTION.value,
            "due_date": cls.Action.UPDATE_DUE_DATE.value,
            "status": cls.Action.UPDATE_STATUS.value,
        }
        for field, action in field_action_mapping.items():
            if field in data:
                old_value = getattr(card, field)
                new_value = data[field]
                if str(new_value) != str(old_value):
                    cls.create_activity_for_update(
                        card, action, user, old_value, new_value
                    )

    @classmethod
    def create_activity_for_update(
        cls, card, action, user, old_value, new_value
    ):
        """
        Method to create activities when a given card attribute is changed.
        """
        if isinstance(old_value, date):
            old_value = str(old_value)
        context = None
        if action != cls.Action.UPDATE_DESCRIPTION:
            context = {
                "old": old_value,
                "new": new_value,
            }
        Activity.objects.create(
            action=action,
            created_by=user,
            card=card,
            context=context,
        )

    @classmethod
    def create_activity_for_tags(cls, card, user, old_tags, new_tags):
        """
        Method to create activities when tag set is changed.
        """
        added_tags = new_tags.difference(old_tags)
        removed_tags = old_tags.difference(new_tags)
        for action, tags in {
            cls.Action.ADD_TAG: added_tags,
            cls.Action.REMOVE_TAG: removed_tags,
        }.items():
            for tag in tags:
                Activity.objects.create(
                    action=action,
                    created_by=user,
                    card=card,
                    context={"tag": tag.name},
                )

    @classmethod
    def create_activity_for_assigned_users(
        cls, card, user, old_users, new_users
    ):
        """
        Method to create activities when assigned user set is changed.
        """
        added_users = new_users.difference(old_users)
        removed_users = old_users.difference(new_users)
        for action, users in {
            cls.Action.ADD_ASSIGNED_USER: added_users,
            cls.Action.REMOVE_ASSIGNED_USER: removed_users,
        }.items():
            for _user in users:
                Activity.objects.create(
                    action=action,
                    created_by=user,
                    card=card,
                    context={"assignee": _user.username},
                )

    @classmethod
    def create_activity_for_timer(cls, card, user, start=True, duration=None):
        """
        Method to create activities when timer is started or stopped.
        """
        action = (
            Activity.Action.START_TIMER if start else Activity.Action.STOP_TIMER
        )
        activity = Activity(
            action=action,
            created_by=user,
            card=card,
        )
        if start is False:
            activity.context = {"duration": str(duration)}
        activity.save()

    @classmethod
    def create_activity_for_time_entry(
        cls, card, user, update=True, old=None, new=None
    ):
        """
        Method to create activities when time entries are updated or removed
        """
        action = (
            cls.Action.UPDATE_TIME_ENTRY
            if update
            else cls.Action.DELETE_TIME_ENTRY
        )
        activity = Activity(
            action=action,
            created_by=user,
            card=card,
        )
        if update:
            if str(old) == str(new):
                return
            activity.context = {
                "old": str(old),
                "new": str(new),
            }
        activity.save()

    @classmethod
    def create_activity_for_comment(cls, card, user, action):
        """
        Method to create activities when comments are added, updated or removed.
        """
        if action not in ("add", "update", "remove"):
            raise ValueError("Invalid action")
        if action == "add":
            action = cls.Action.ADD_COMMENT
        if action == "update":
            action = cls.Action.UPDATE_COMMENT
        if action == "remove":
            action = cls.Action.REMOVE_COMMENT
        Activity.objects.create(
            action=action,
            created_by=user,
            card=card,
        )

    @classmethod
    def create_activity_for_file(cls, card, user, add=True):
        """
        Method to create activities when files are added or removed
        """
        Activity.objects.create(
            action=cls.Action.ADD_FILE if add else cls.Action.REMOVE_FILE,
            created_by=user,
            card=card,
        )

    @classmethod
    def create_activity_for_checklist(
        cls, card, user, action, value=None, new_value=None
    ):
        """
        Method to create activities when checklist items are added, updated or removed
        """
        if action not in ("add", "update", "remove"):
            raise ValueError("Invalid action")
        if action == "add":
            action = cls.Action.ADD_CHECKLIST_ITEM
            context = {
                "item": value,
            }
        if action == "update":
            if value == new_value:
                return
            action = cls.Action.UPDATE_CHECKLIST_ITEM
            context = {
                "old": value,
                "new": new_value,
            }
        if action == "remove":
            action = cls.Action.REMOVE_CHECKLIST_ITEM
            context = {
                "item": value,
            }
        Activity.objects.create(
            action=action, created_by=user, card=card, context=context
        )

    @classmethod
    def create_activity_for_color(cls, card, user, old_value, new_value):
        """
        Method to create activities when color is changed
        """
        if old_value == new_value:
            return
        Activity.objects.create(
            action=cls.Action.UPDATE_COLOR,
            created_by=user,
            card=card,
            context={
                "old": old_value,
                "new": new_value,
            },
        )

    @staticmethod
    def process_color(value: str) -> str:
        return _(value).lower() if value is not None else _("no color")

    @staticmethod
    def process_date(
        value: str,
    ) -> str:  # pylint: disable=inconsistent-return-statements
        """Convert dates from db format to localized"""
        if value is not None:
            date_obj = datetime.strptime(value, "%Y-%m-%d")
            date_str = date_format(
                date_obj, format="SHORT_DATE_FORMAT", use_l10n=True
            )
        else:
            date_str = _("no date")
        return date_str

    @staticmethod
    def process_status(value: str) -> str:
        """Convert status choices from db values to human-readable"""
        for _value, text in Card.Status.choices:
            if value == _value:
                return _(text)
        return None

    @staticmethod
    def noop(value: str) -> str:
        return value

    @property
    def detailed_text(self):
        """
        Output detailed information of this activity
        """
        context = self.context
        if context is None:
            context = {}
        text = ""
        if self.action == Activity.Action.UPDATE_COLOR:
            func = Activity.process_color
        elif self.action == Activity.Action.UPDATE_DUE_DATE:
            func = Activity.process_date
        elif self.action == Activity.Action.UPDATE_STATUS:
            func = Activity.process_status
        else:
            func = Activity.noop
        context = {k: func(v) for k, v in context.items()}
        context["user"] = {
            "username": self.created_by.username,
            "pic": self.created_by.profile.avatar.url,
        }
        context["natural_time"] = NaturalTimeFormatter.string_for(
            self.created_at
        )
        text = f"{self.get_action_display()} %(natural_time)s"
        return {"text": text, "context": context}

    @property
    def verbose_text(self):
        """Human readable text describing the executed action"""
        context = self.context
        if context is None:
            context = {}
        text = ""
        if self.action == Activity.Action.UPDATE_COLOR:
            func = Activity.process_color
        elif self.action == Activity.Action.UPDATE_DUE_DATE:
            func = Activity.process_date
        elif self.action == Activity.Action.UPDATE_STATUS:
            func = Activity.process_status
        else:
            func = Activity.noop
        context = {k: func(v) for k, v in context.items()}
        context["user"] = self.created_by.username
        try:
            text = self.get_action_display() % context
        except TypeError:
            text = self.get_action_display()
        natural_time = NaturalTimeFormatter.string_for(self.created_at)
        return _("%(executed_action)s %(natural_time)s") % {
            "executed_action": text,
            "natural_time": natural_time,
        }


class Card(BaseModel):
    """
    Card, main entity, holds information about tasks
    """

    def _card_directory_path(self, filename):
        """file will be uploaded to MEDIA_ROOT/project_<id>/<filename>"""
        p_id = self.bucket.board.project.id
        return f"project_{p_id}/{filename}"

    class Status(models.TextChoices):
        """
        Status choices for card
        """

        NOT_STARTED = Bucket.NOT_STARTED, _("Not started")
        IN_PROGRESS = Bucket.IN_PROGRESS, _("In progress")
        COMPLETED = Bucket.COMPLETED, _("Completed")

    class TimerActions(models.TextChoices):
        """Timer actions"""

        START = "start"
        STOP = "stop"
        NONE = "none"

    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
    order = models.IntegerField()
    assigned_to = models.ManyToManyField(
        User, related_name="assigned_cards", blank=True
    )
    description = models.TextField(max_length=1000, blank=True, null=True)
    status = models.CharField(
        _("status"),
        max_length=2,
        choices=Status.choices,
        default=Bucket.NOT_STARTED,
    )
    due_date = models.DateField(blank=True, null=True, default=None)
    started_at = models.DateTimeField(blank=True, null=True)
    started_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="started_cards",
        blank=True,
        null=True,
    )
    completed_at = models.DateTimeField(blank=True, null=True)
    completed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="completed_cards",
        blank=True,
        null=True,
    )
    color = models.ForeignKey(
        "Theme", on_delete=models.CASCADE, blank=True, null=True, default=None
    )
    tag = models.ManyToManyField(Tag, blank=True, default=None)

    # @transaction.atomic
    def set_order(self, bucket, order):
        """
        Set card order
        """
        same_bucket = self.bucket == bucket
        if not same_bucket:
            _bucket = self.bucket
            self.bucket = bucket
        self.order = order
        self.save()
        cards = Card.objects.filter(bucket=bucket).exclude(id=self.id)
        for i, card in enumerate(cards):
            if i + 1 < order:
                card.order = i + 1
                card.save()
            else:
                card.order = i + 2
                card.save()
        self.bucket.touch()
        if not same_bucket:
            _bucket.sort()
            _bucket.touch()

    def mark_as_completed(self, user):
        """Mark card as completed"""
        self.status = Bucket.COMPLETED
        self.completed_at = timezone.now()
        self.completed_by = user
        self.save()

    def mark_as_in_progress(self, user):
        """Mark card as in progress"""
        self.status = Bucket.IN_PROGRESS
        self.started_at = timezone.now()
        self.started_by = user
        self.completed_at = None
        self.completed_by = None
        self.save()

    def mark_as_not_started(self):
        """Mark card as not started"""
        self.status = Bucket.NOT_STARTED
        self.started_at = None
        self.started_by = None
        self.completed_at = None
        self.completed_by = None
        self.save()

    @property
    def allowed_users(self):
        return self.bucket.board.allowed_users

    @property
    def is_running(self):
        return self.timeentry_set.filter(stopped_at__isnull=True).exists()

    @property
    def total_time(self):
        """Total time tracked for this card"""
        stopped_entries = self.timeentry_set.filter(stopped_at__isnull=False)
        running_entries = self.timeentry_set.filter(stopped_at__isnull=True)
        stopped_entries_duration = stopped_entries.aggregate(
            duration=Coalesce(
                Sum("duration"), V(timedelta(0)), output_field=DurationField()
            )
        )["duration"]
        running_entries_duration = sum(
            [timezone.now() - entry.started_at for entry in running_entries],
            timedelta(),
        )
        return stopped_entries_duration + running_entries_duration

    # @transaction.atomic
    def start_timer(self, user):
        """
        Create new time entry if no running entry is found.
        """
        running_time_entries = self.timeentry_set.filter(
            stopped_at__isnull=True
        )
        if running_time_entries.exists():
            return {"action": self.TimerActions.NONE}
        time_entry = TimeEntry.objects.create(
            name="Time entry",
            card=self,
            started_at=timezone.now(),
            created_by=user,
        )
        time_entry.card.bucket.touch()
        Activity.create_activity_for_timer(self, user)
        return {"action": self.TimerActions.START}

    # @transaction.atomic
    def stop_timer(self, user):
        """
        Stop any running time entry.
        """
        running_time_entries = self.timeentry_set.filter(
            stopped_at__isnull=True
        )
        if running_time_entries.exists():
            for time_entry in running_time_entries:
                time_entry.stopped_at = timezone.now()
                time_entry.save()
                time_entry.card.bucket.touch()
                Activity.create_activity_for_timer(
                    self, user, False, time_entry.duration
                )
            return {"action": self.TimerActions.STOP}
        return {"action": self.TimerActions.NONE}

    def start_stop_timer(self, user):
        """
        Toggle timer
        """
        result = self.stop_timer(user)
        if result["action"] != self.TimerActions.NONE:
            return result
        return self.start_timer(user)

    @property
    def max_order(self):
        return self.item_set.all().aggregate(
            max_order=Coalesce(Max("order"), V(0), output_field=IntegerField())
        )["max_order"]

    @property
    def checked_items(self):
        return self.item_set.filter(checked_at__isnull=False).count()

    @property
    def total_items(self):
        return self.item_set.all().count()

    @property
    def total_files(self):
        return self.files.all().count()

    @property
    def comments(self):
        return self.comment_set.all().count()

    class Meta:
        ordering = [
            "bucket__board__project",
            "bucket__board",
            "bucket",
            "order",
        ]


class CardFile(models.Model):
    """File stored in card"""

    def _card_directory_path(self, filename):
        """Format path to store card files"""
        p_id = self.card.bucket.board.project.id
        b_id = self.card.bucket.board.id
        return f"project_{p_id}/board_{b_id}/{filename}"

    file = models.FileField(upload_to=_card_directory_path, max_length=1000)
    card = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name="files"
    )

    @property
    def image(self):
        """
        Get image type
        """
        try:
            img = imghdr.what(self.file)
        except OSError:
            img = None
        return img

    @property
    def extension(self):
        """
        Get file extension
        """
        try:
            _, extension = os.path.splitext(self.file.name)
        except OSError:
            extension = ""
        return extension


class Item(BaseModel):
    """
    Checklist item in a card
    """

    order = models.IntegerField()
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    checked_at = models.DateTimeField(null=True, blank=True, default=None)
    checked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="checked_items",
        default=None,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            "order",
        ]

    @property
    def checked(self):
        return self.checked_at is not None

    @property
    def allowed_users(self):
        return self.card.bucket.board.allowed_users

    def mark_as_checked(self, user):
        """Mark item as checked"""
        self.checked_at = timezone.now()
        self.checked_by = user
        self.save()

    def mark_as_unchecked(self):
        """Mark item as unchecked"""
        self.checked_at = None
        self.checked_by = None
        self.save()


class Comment(models.Model):
    """Comment in a card"""

    text = models.TextField(max_length=1000, null=False, blank=False)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="card_comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.text

    class Meta:
        ordering = ["created_at"]

    @property
    def allowed_users(self):
        return self.card.bucket.board.allowed_users

    @property
    def mentioned_users(self):
        """Get users referenced in comment text"""
        users = []
        for match in re.finditer("@", self.text):
            space = self.text.find(" ", match.start() + 1)
            if match.start() > 0:
                previous_char = self.text[match.start() - 1]
                if previous_char not in [" ", "\n"]:
                    continue
            if space != -1:
                username = self.text[match.start() + 1 : space]
            else:
                username = self.text[match.start() + 1 :]
            try:
                user = User.objects.get(username=username)
                users.append(user)
            except User.DoesNotExist:
                pass
        return users

    def notify_mentioned_users(self):
        """Send email to mentioned users"""
        text = get_template("email/card_comment.txt")
        html = get_template("email/card_comment.html")

        site = settings.SITE

        full_link = f"{site}/card"

        context = {
            "mention": True,
            "card": self.card.name,
            "author": self.created_by.username,
            "comment": self.text,
            "link": full_link,
        }

        subject, from_email = _("Comment"), settings.EMAIL_HOST_USER
        for user in self.mentioned_users:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text.render(context),
                from_email=from_email,
                to=[user.email],
            )
            context["user"] = user.username
            msg.attach_alternative(html.render(context), "text/html")
            msg.send(fail_silently=False)
            Notification.objects.create(
                title=_("Comment on card"),
                message=_("Someone commented on a card and mentioned you."),
                icon="exclamation",
                to=user,
                action_url=full_link,
            )

    def notify_assignees(self):
        """Send email to assignee"""

        text = get_template("email/card_comment.txt")
        html = get_template("email/card_comment.html")

        site = settings.SITE

        full_link = f"{site}/card"

        context = {
            "mention": False,
            "card": self.card.name,
            "author": self.created_by.username,
            "comment": self.text,
            "link": full_link,
        }

        subject, from_email = _("Comment"), settings.EMAIL_HOST_USER
        for user in self.card.assigned_to.exclude(id=self.created_by.id):
            if user in self.mentioned_users:
                continue
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text.render(context),
                from_email=from_email,
                to=[user.email],
            )
            context["user"] = user.username
            msg.attach_alternative(html.render(context), "text/html")
            msg.send(fail_silently=False)
            Notification.objects.create(
                title=_("Comment on card"),
                message=_("Someone commented on a card assigned to you."),
                icon="exclamation",
                to=user,
                action_url=full_link,
            )


class TimeEntry(BaseModel):
    """Time entry in a card"""

    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    stopped_at = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True, editable=False)

    class Meta:
        verbose_name = _("time entry")
        verbose_name_plural = _("time entries")

    @property
    def is_running(self):
        return self.stopped_at is None

    @property
    def is_stopped(self):
        return self.stopped_at is not None

    @property
    def allowed_users(self):
        return self.card.bucket.board.allowed_users


class Theme(models.Model):
    """
    Color theme of cards or boards
    """

    DEFAULT_THEMES = [
        ("Red", "#f44336", "#b71c1c", "#ffebee"),
        ("Orange", "#ff9800", "#e65100", "#fff3e0"),
        ("Yellow", "#ffeb3b", "#f57f17", "#fffde7"),
        ("Olive", "#cddc39", "#827717", "#f9fbe7"),
        ("Green", "#4caf50", "#1b5e20", "#e8f5e9"),
        ("Teal", "#009688", "#004d40", "#e0f2f1"),
        ("Blue", "#2196f3", "#2185d0", "#e3f2fd"),
        ("Violet", "#673ab7", "#311b92", "#ede7f6"),
        ("Purple", "#9c27b0", "#a333c8", "#f3e5f5"),
        ("Pink", "#e91e63", "#880e4f", "#fce4ec"),
        ("Brown", "#795548", "#3e2723", "#efebe9"),
        ("Grey", "#9e9e9e", "#212121", "#fafafa"),
        ("Black", "#263238", "#000a12", "#eceff1"),
    ]
    name = models.CharField(_("name"), max_length=50, unique=True)
    primary = models.CharField(_("primary"), max_length=7)
    dark = models.CharField(_("dark"), max_length=7)
    light = models.CharField(_("light"), max_length=7)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def create_defaults(cls):
        """
        Create default themes
        """
        themes = [
            cls(name=n, primary=p, dark=d, light=l)
            for n, p, d, l in cls.DEFAULT_THEMES
        ]
        cls.objects.bulk_create(themes, ignore_conflicts=True)


class Icon(models.Model):
    """
    Icon used for tags
    """

    markup = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.markup

    @classmethod
    def create_defaults(cls):
        """Create default icons"""
        icons = [cls(markup=markup) for markup in DEFAULT_ICONS]
        cls.objects.bulk_create(icons, ignore_conflicts=True)

    class Meta:
        verbose_name = _("icon")
        verbose_name_plural = _("icons")


class Invite(models.Model):
    """Invite to assign user to project"""

    email = models.EmailField(max_length=1000, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
        related_name="created_project_invites",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
        related_name="accepted_project_invites",
    )
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("invite")
        verbose_name_plural = _("invites")

    @property
    def accepted(self):
        return self.accepted_by is not None

    def accept(self, user):
        """
        Accept invite
        """
        project = self.project
        project.assigned_to.add(user)
        self.accepted_by = user
        self.accepted_at = timezone.now()
        self.save()
        Notification.objects.create(
            title="Project invitation",
            message=f"{user} accepted your invite.",
            icon="exclamation",
            to=self.created_by,
            action_url=reverse(
                "project_manager:project_detail", args=[project.id]
            ),
        )

    @property
    def link(self):
        """
        Display valid link to accept invite
        """
        signer = TimestampSigner(salt="project_invite")
        token = signer.sign_object(
            {
                "id": self.id,
            }
        )
        return f"{settings.SITE}{reverse('project_manager:invite_acceptance')}?t={token}"

    def send(self):
        """
        Send invite via email
        """
        text = get_template("email/invitation.txt")
        html = get_template("email/invitation.html")

        context = {"site": settings.SITE, "link": self.link}

        msg = EmailMultiAlternatives(
            subject=_("Invite"),
            body=text.render(context),
            from_email=settings.EMAIL_HOST_USER,
            to=[self.email],
        )
        msg.attach_alternative(html.render(context), "text/html")
        msg.send(fail_silently=False)
        if User.objects.filter(email=self.email).exists():
            Notification.objects.create(
                title=_("Project invitation"),
                message=_("You were invited to be part of a project."),
                icon="exclamation",
                to=User.objects.get(email=self.email),
                action_url=self.link,
            )

    def __str__(self) -> str:
        return f"{str(self.project)} -> {self.email}"

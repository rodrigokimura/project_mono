from datetime import timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.aggregates import Max
from django.db.models.fields import IntegerField
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum, Value as V, DurationField
from django.db.models.functions import Coalesce


User = get_user_model()


def card_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class BaseModel(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = True


class Project(BaseModel):
    deadline = models.DateTimeField()
    # milestones =
    assigned_to = models.ManyToManyField(User, related_name="assigned_projects")

    @property
    def allowed_users(self):
        return self.assigned_to.union(User.objects.filter(id=self.created_by.id))


class Board(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(User, related_name="assigned_boards")

    @property
    def allowed_users(self):
        return self.assigned_to.union(User.objects.filter(id=self.created_by.id))

    @property
    def max_order(self):
        return self.bucket_set.all().aggregate(
            max_order=Coalesce(Max('order'), V(0), output_field=IntegerField())
        )['max_order']


class Bucket(BaseModel):
    DEFAULT_BUCKETS = [
        (_('To do'), _('Stuff to do'), 1),
        (_('Doing'), _('Stuff being done'), 2),
        (_('Done'), _('Stuff already finished'), 3),
    ]
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    order = models.IntegerField()
    description = models.TextField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = [
            "board__project",
            "board",
            "order",
        ]

    @property
    def max_order(self):
        return self.card_set.all().aggregate(
            max_order=Coalesce(Max('order'), V(0), output_field=IntegerField())
        )['max_order']

    def sort(self):
        for index, card in enumerate(self.card_set.all()):
            card.order = index + 1
            card.save()


class Card(BaseModel):
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
    order = models.IntegerField()
    assigned_to = models.ManyToManyField(User, related_name="assigned_cards", blank=True)
    description = models.TextField(max_length=255, blank=True, null=True)
    files = models.FileField(upload_to=None, max_length=100, blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    completed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="completed_cards", blank=True, null=True)

    @property
    def allowed_users(self):
        return self.bucket.board.allowed_users

    @property
    def is_running(self):
        return self.timeentry_set.filter(stopped_at__isnull=True).exists()

    @property
    def total_time(self):
        stopped_entries = self.timeentry_set.filter(
            stopped_at__isnull=False
        )
        running_entries = self.timeentry_set.filter(
            stopped_at__isnull=True
        )
        stopped_entries_duration = stopped_entries.aggregate(
            duration=Coalesce(Sum("duration"), V(0), output_field=DurationField())
        )['duration']
        running_entries_duration = sum([timezone.now() - entry.started_at for entry in running_entries], timedelta())
        return stopped_entries_duration + running_entries_duration

    def start_stop_timer(self, user):
        running_time_entries = self.timeentry_set.filter(stopped_at__isnull=True)
        if running_time_entries.exists():
            for time_entry in running_time_entries:
                time_entry.stopped_at = timezone.now()
                time_entry.save()
            return {'action': 'stop'}
        else:
            TimeEntry.objects.create(
                name="Time entry",
                card=self,
                started_at=timezone.now(),
                created_by=user
            )
            return {'action': 'start'}

    class Meta:
        ordering = [
            "bucket__board__project",
            "bucket__board",
            "bucket",
            "order",
        ]


class Item(BaseModel):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    checked_at = models.DateTimeField()
    checked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checked_items")


class TimeEntry(BaseModel):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    stopped_at = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True, editable=False)

    class Meta:
        verbose_name = _("time entry")
        verbose_name_plural = _("time entries")

    @property
    def is_running(self):
        return self.stopped_at is None

    @property
    def is_stoppped(self):
        return self.stopped_at is not None

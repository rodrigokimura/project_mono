"""Checklists' models"""
from datetime import timedelta

from accounts.models import Notification
from background_task.models import Task as BackgroundTask
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from .tasks import create_next_task, remind

User = get_user_model()


class Checklist(models.Model):
    """Checklist"""
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checklists")
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['created_by', 'order']

    def __str__(self) -> str:
        return self.name

    def sort(self):
        """Fix task order"""
        for index, task in enumerate(self.task_set.all()):
            task.order = index + 1
            task.save()

    @property
    def max_count(self):
        return self.task_set.all().count()

    @transaction.atomic
    def set_order(self, order):
        checklists = Checklist.objects.filter(created_by=self.created_by).exclude(id=self.id)
        for i, checklist in enumerate(checklists):
            if i + 1 < order:
                checklist.order = i + 1
                checklist.save()
            else:
                checklist.order = i + 2
                checklist.save()
        self.order = order
        self.save()


class Task(models.Model):
    """Checklist item"""

    class Recurrence(models.TextChoices):
        """Frequency choices"""
        DAILY = 'daily', _('Daily')
        WEEKLY = 'weekly', _('Weekly')
        MONTHLY = 'monthly', _('Monthly')
        YEARLY = 'yearly', _('Yearly')

    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    note = models.TextField(default='', max_length=2000)
    order = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_checklist_tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    checked_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="checked_checklist_tasks",
        null=True,
        blank=True
    )
    checked_at = models.DateTimeField(null=True, blank=True)
    reminder = models.DateTimeField(null=True, blank=True, default=None)
    reminded = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True, default=None)
    recurrence = models.CharField(max_length=7, null=True, blank=True, choices=Recurrence.choices)
    next_task_created = models.BooleanField(default=False)

    class Meta:
        ordering = ['checklist', 'order']

    def __str__(self) -> str:
        return self.description

    @transaction.atomic
    def set_order(self, order):
        tasks = Task.objects.filter(checklist=self.checklist).exclude(id=self.id)
        for i, task in enumerate(tasks):
            if i + 1 < order:
                task.order = i + 1
                task.save()
            else:
                task.order = i + 2
                task.save()
        self.order = order
        self.save()

    def schedule_reminder(self):
        BackgroundTask.objects.drop_task(task_name='checklists.tasks.remind', args=[self.id])
        if self.reminder is not None and not self.reminded:
            remind(self.id, schedule=self.reminder)

    def mark_as_checked(self, user):
        """Mark task as checked"""
        self.checked_by = user
        self.checked_at = now()
        self.save()

    def mark_as_unchecked(self):
        """Mark task as unchecked"""
        self.checked_by = None
        self.checked_at = None
        self.save()

    def remind(self):
        """Remind task"""
        if self.reminder and not self.reminded:
            Notification.objects.create(
                title=_('Reminder for task'),
                message=_('You have a task to do: %(description)s') % {'description': self.description},
                to=self.created_by,
                action_url=reverse('checklists:index'),
            )
            self.reminded = True
            self.save()

    def schedule_recurrent_task(self):
        """Schedule creation of next task"""
        BackgroundTask.objects.drop_task(task_name='checklists.tasks.create_next_task', args=[self.id])
        run_at = self.get_next_due_date()
        if self.recurrence and not self.next_task_created:
            create_next_task(self.pk, schedule=run_at, creator=self)

    def get_next_due_date(self):
        if self.recurrence == self.Recurrence.DAILY:
            increment = timedelta(days=1)
        elif self.recurrence == self.Recurrence.WEEKLY:
            increment = timedelta(days=7)
        elif self.recurrence == self.Recurrence.MONTHLY:
            increment = relativedelta(months=1)
        elif self.recurrence == self.Recurrence.YEARLY:
            increment = relativedelta(years=1)
        else:
            raise NotImplementedError('Invalid task recurrence')
        d = self.due_date
        while True:
            d += increment
            if d > now():
                return d

    @transaction.atomic()
    def create_next_task(self):
        if self.recurrence is None:
            return
        checklist: Checklist = self.checklist
        task = Task(
            checklist=checklist,
            description=self.description,
            note=self.note,
            order=checklist.max_count + 1,
            created_by=self.created_by,
            due_date=self.get_next_due_date(),
            recurrence=self.recurrence,
        )
        task.save()
        self.next_task_created = True
        self.save()


class Configuration(models.Model):
    """Store user configuration"""
    show_completed_tasks = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.OneToOneField(User, on_delete=models.CASCADE, related_name="checklists_config")
    updated_at = models.DateTimeField(auto_now=True)

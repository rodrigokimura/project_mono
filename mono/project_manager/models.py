import os
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.aggregates import Max
from django.db.models.fields import IntegerField
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum, Value as V, DurationField
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
import jwt
import re
from datetime import timedelta
import imghdr


User = get_user_model()


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
    deadline = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ManyToManyField(User, related_name="assigned_projects", blank=True)

    @property
    def allowed_users(self):
        return (User.objects.filter(id=self.created_by.id) | self.assigned_to.all()).distinct()

    class Meta:
        ordering = [
            "created_at",
        ]


class Board(BaseModel):

    def _background_image_path(instance, filename):
        return 'project_{0}/board_{1}/{2}'.format(instance.project.id, instance.id, filename)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(User, related_name="assigned_boards", blank=True)
    fullscreen = models.BooleanField(default=False)
    compact = models.BooleanField(default=False)
    dark = models.BooleanField(default=False)
    bucket_width = models.IntegerField(default=300)
    updated_at = models.DateTimeField(auto_now=True)
    background_image = models.ImageField(upload_to=_background_image_path, blank=True, null=True)

    @property
    def allowed_users(self):
        return (User.objects.filter(id=self.created_by.id) | self.assigned_to.all()).distinct()

    @property
    def max_order(self):
        return self.bucket_set.all().aggregate(
            max_order=Coalesce(Max('order'), V(0), output_field=IntegerField())
        )['max_order']

    def touch(self):
        self.save()

    class Meta:
        ordering = [
            "project",
            "created_at",
        ]


class Bucket(BaseModel):
    NONE = 'N'
    NOT_STARTED = 'NS'
    IN_PROGRESS = 'IP'
    COMPLETED = 'C'
    STATUSES = [
        (NONE, _('No automatic status')),
        (NOT_STARTED, _('Not started')),
        (IN_PROGRESS, _('In progress')),
        (COMPLETED, _('Completed')),
    ]
    DEFAULT_BUCKETS = [
        (_('To do'), _('Stuff to do'), 1, NOT_STARTED),
        (_('Doing'), _('Stuff being done'), 2, IN_PROGRESS),
        (_('Done'), _('Stuff already finished'), 3, COMPLETED),
    ]
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    order = models.IntegerField()
    description = models.TextField(max_length=255, blank=True, null=True)
    auto_status = models.CharField(_("status"), max_length=2, choices=STATUSES, default=NONE)
    color = models.ForeignKey('Theme', on_delete=models.CASCADE, blank=True, null=True, default=None)
    updated_at = models.DateTimeField(auto_now=True)

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

    def touch(self):
        self.save()

    def sort(self):
        for index, card in enumerate(self.card_set.all()):
            card.order = index + 1
            card.save()


class Tag(BaseModel):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    icon = models.ForeignKey('Icon', on_delete=models.SET_NULL, default=None, null=True, blank=True)
    color = models.ForeignKey('Theme', on_delete=models.SET_NULL, default=None, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['board', 'name'], name='unique_tag'),
        ]


class Card(BaseModel):

    def _card_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/project_<id>/<filename>
        return 'project_{0}/{1}'.format(instance.bucket.board.project.id, filename)

    STATUSES = [
        (Bucket.NOT_STARTED, _('Not started')),
        (Bucket.IN_PROGRESS, _('In progress')),
        (Bucket.COMPLETED, _('Completed')),
    ]

    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
    order = models.IntegerField()
    assigned_to = models.ManyToManyField(User, related_name="assigned_cards", blank=True)
    description = models.TextField(max_length=255, blank=True, null=True)
    status = models.CharField(_("status"), max_length=2, choices=STATUSES, default=Bucket.NOT_STARTED)
    due_date = models.DateField(blank=True, null=True, default=None)
    started_at = models.DateTimeField(blank=True, null=True)
    started_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="started_cards", blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    completed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="completed_cards", blank=True, null=True)
    color = models.ForeignKey('Theme', on_delete=models.CASCADE, blank=True, null=True, default=None)
    tag = models.ManyToManyField(Tag, blank=True, default=None)

    def mark_as_completed(self, user):
        self.status = Bucket.COMPLETED
        self.completed_at = timezone.now()
        self.completed_by = user
        self.save()

    def mark_as_in_progress(self, user):
        self.status = Bucket.IN_PROGRESS
        self.started_at = timezone.now()
        self.started_by = user
        self.completed_at = None
        self.completed_by = None
        self.save()

    def mark_as_not_started(self):
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

    def start_timer(self, user):
        """
            Create new time entry if no running entry is found.
        """
        running_time_entries = self.timeentry_set.filter(stopped_at__isnull=True)
        if running_time_entries.exists():
            return {'action': 'none'}
        else:
            time_entry = TimeEntry.objects.create(
                name="Time entry",
                card=self,
                started_at=timezone.now(),
                created_by=user
            )
            time_entry.card.bucket.touch()
            return {'action': 'start'}

    def stop_timer(self):
        """
            Stop any running time entry.
        """
        running_time_entries = self.timeentry_set.filter(stopped_at__isnull=True)
        if running_time_entries.exists():
            for time_entry in running_time_entries:
                time_entry.stopped_at = timezone.now()
                time_entry.save()
                time_entry.card.bucket.touch()
            return {'action': 'stop'}
        else:
            return {'action': 'none'}

    def start_stop_timer(self, user):
        running_time_entries = self.timeentry_set.filter(stopped_at__isnull=True)
        if running_time_entries.exists():
            for time_entry in running_time_entries:
                time_entry.stopped_at = timezone.now()
                time_entry.save()
                time_entry.card.bucket.touch()
            return {'action': 'stop'}
        else:
            time_entry = TimeEntry.objects.create(
                name="Time entry",
                card=self,
                started_at=timezone.now(),
                created_by=user
            )
            time_entry.card.bucket.touch()
            return {'action': 'start'}

    @property
    def max_order(self):
        return self.item_set.all().aggregate(
            max_order=Coalesce(Max('order'), V(0), output_field=IntegerField())
        )['max_order']

    @property
    def checked_items(self):
        return self.item_set.filter(checked_at__isnull=False).count()

    @property
    def total_items(self):
        return self.item_set.all().count()

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

    def _card_directory_path(instance, filename):
        return 'project_{0}/board_{1}/{2}'.format(
            instance.card.bucket.board.project.id,
            instance.card.bucket.board.id,
            filename
        )

    file = models.FileField(upload_to=_card_directory_path, max_length=1000, blank=True, null=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='files')

    @property
    def image(self):
        try:
            img = imghdr.what(self.file)
        except:
            img = None 
        return img

    @property
    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension


class Item(BaseModel):
    order = models.IntegerField()
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    checked_at = models.DateTimeField(null=True, blank=True, default=None)
    checked_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="checked_items", default=None, null=True, blank=True)

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
        self.checked_at = timezone.now()
        self.checked_by = user
        self.save()

    def mark_as_unchecked(self):
        self.checked_at = None
        self.checked_by = None
        self.save()


class Comment(models.Model):
    text = models.TextField(max_length=1000, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="card_comments")
    created_at = models.DateTimeField(auto_now_add=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.text

    class Meta:
        ordering = ['created_at']

    @property
    def allowed_users(self):
        return self.card.bucket.board.allowed_users

    @property
    def mentioned_users(self):
        users = []
        for m in re.finditer('@', self.text):
            space = self.text.find(' ', m.start() + 1)
            if m.start() > 0:
                previous_char = self.text[m.start() - 1]
                if previous_char not in [' ', '\n']:
                    continue
            if space != -1:
                username = self.text[m.start() + 1:space]
            else:
                username = self.text[m.start() + 1:]
            print(username)
            try:
                user = User.objects.get(username=username)
                users.append(user)
            except User.DoesNotExist:
                pass
        return users

    def notify_mentioned_users(self):
        text = get_template('email/card_comment.txt')
        html = get_template('email/card_comment.html')

        site = settings.SITE

        full_link = f"{site}/card"

        context = {
            'mention': True,
            'card': self.card.name,
            'author': self.created_by.username,
            'comment': self.text,
            'link': full_link,
        }

        subject, from_email = _('Comment'), settings.EMAIL_HOST_USER
        for user in self.mentioned_users:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text.render(context),
                from_email=from_email,
                to=[user.email])
            context['user'] = user.username
            msg.attach_alternative(html.render(context), "text/html")
            msg.send(fail_silently=False)
            Notification.objects.create(
                title=_("Comment on card"),
                message=_("Someone commented on a card and mentioned you."),
                icon=Icon.objects.get(markup="exclamation"),
                to=user,
                action=full_link
            )

    def notify_assignees(self):

        text = get_template('email/card_comment.txt')
        html = get_template('email/card_comment.html')

        site = settings.SITE

        full_link = f"{site}/card"

        context = {
            'mention': False,
            'card': self.card.name,
            'author': self.created_by.username,
            'comment': self.text,
            'link': full_link,
        }

        subject, from_email = _('Comment'), settings.EMAIL_HOST_USER
        for user in self.card.assigned_to.exclude(id=self.created_by.id):
            if user in self.mentioned_users:
                continue
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text.render(context),
                from_email=from_email,
                to=[user.email])
            context['user'] = user.username
            msg.attach_alternative(html.render(context), "text/html")
            msg.send(fail_silently=False)
            Notification.objects.create(
                title=_("Comment on card"),
                message=_("Someone commented on a card assigned to you."),
                icon=Icon.objects.get(markup="exclamation"),
                to=user,
                action=full_link
            )


class TimeEntry(BaseModel):
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
    DEFAULT_THEMES = [
        ('Red', '#f44336', '#b71c1c', '#ffebee'),
        ('Orange', '#ff9800', '#e65100', '#fff3e0'),
        ('Yellow', '#ffeb3b', '#f57f17', '#fffde7'),
        ('Olive', '#cddc39', '#827717', '#f9fbe7'),
        ('Green', '#4caf50', '#1b5e20', '#e8f5e9'),
        ('Teal', '#009688', '#004d40', '#e0f2f1'),
        ('Blue', '#2196f3', '#2185d0', '#e3f2fd'),
        ('Violet', '#673ab7', '#311b92', '#ede7f6'),
        ('Purple', '#9c27b0', '#a333c8', '#f3e5f5'),
        ('Pink', '#e91e63', '#880e4f', '#fce4ec'),
        ('Brown', '#795548', '#3e2723', '#efebe9'),
        ('Grey', '#9e9e9e', '#212121', '#fafafa'),
        ('Black', '#263238', '#000a12', '#eceff1'),
    ]
    name = models.CharField(_('name'), max_length=50, unique=True)
    primary = models.CharField(_('primary'), max_length=7)
    dark = models.CharField(_('dark'), max_length=7)
    light = models.CharField(_('light'), max_length=7)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    def _create_defaults():
        for theme in Theme.DEFAULT_THEMES:
            Theme.objects.update_or_create(
                name=theme[0],
                defaults={
                    'primary': theme[1],
                    'dark': theme[2],
                    'light': theme[3],
                }
            )


class Icon(models.Model):
    DEFAULT_ICONS = [
        'home',
        'exclamation',
    ]
    markup = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.markup

    def _create_defaults():
        for markup in Icon.DEFAULT_ICONS:
            Icon.objects.update_or_create(markup=markup)

    class Meta:
        verbose_name = _("icon")
        verbose_name_plural = _("icons")


class Notification(models.Model):
    title = models.CharField(max_length=50)
    message = models.CharField(max_length=255)
    icon = models.ForeignKey(Icon, on_delete=models.SET_NULL, null=True, default=None)
    to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_manager_notifications")
    read_at = models.DateTimeField(blank=True, null=True, default=None)
    action = models.CharField(max_length=1000, blank=True, null=True, default=None)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")

    def __str__(self) -> str:
        return self.title

    @property
    def read(self):
        return self.read_at is not None

    def mark_as_read(self):
        self.read_at = timezone.now()
        self.save()

    def set_icon_by_markup(self, markup):
        self.icon = Icon.objects.filter(markup=markup).first()
        self.save()


class Invite(models.Model):
    email = models.EmailField(max_length=1000, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, default=None, null=True, blank=True, related_name="created_project_invites")
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_by = models.ForeignKey(User, on_delete=models.SET_NULL, default=None, null=True, blank=True, related_name="accepted_project_invites")
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("invite")
        verbose_name_plural = _("invites")

    @property
    def accepted(self):
        return self.accepted_by is not None

    def accept(self, user):
        project = self.project
        project.assigned_to.add(user)
        self.accepted_by = user
        self.accepted_at = timezone.now()
        self.save()
        Notification.objects.create(
            title="Project invitation",
            message=f"{user} accepted your invite.",
            icon=Icon.objects.get(markup="exclamation"),
            to=self.created_by,
            action=reverse("project_manager:project_detail", args=[project.id]),
        )

    @property
    def link(self):
        token = jwt.encode(
            {
                "exp": timezone.now() + timedelta(days=1),
                "id": self.pk,
            },
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        site = settings.SITE
        return f"{site}{reverse('project_manager:invite_acceptance')}?t={token}"

    def send(self):

        template_html = 'email/invitation.html'
        template_text = 'email/invitation.txt'

        text = get_template(template_text)
        html = get_template(template_html)

        site = settings.SITE

        full_link = self.link

        d = {
            'site': site,
            'link': full_link
        }

        subject, from_email, to = _('Invite'), settings.EMAIL_HOST_USER, self.email
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text.render(d),
            from_email=from_email,
            to=[to])
        msg.attach_alternative(html.render(d), "text/html")
        msg.send(fail_silently=False)
        if User.objects.filter(email=self.email).exists():
            Notification.objects.create(
                title=_("Project invitation"),
                message=_("You were invited to be part of a project."),
                icon=Icon.objects.get(markup="exclamation"),
                to=User.objects.get(email=self.email),
                action=full_link
            )

    def __str__(self) -> str:
        return f'{str(self.project)} -> {self.email}'

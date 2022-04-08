"""Notes' models"""
from django.contrib.auth import get_user_model
from django.db import models
from django.urls.base import reverse
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField

User = get_user_model()


def user_directory_path(instance, filename):
    """file will be uploaded to MEDIA_ROOT/user_<id>/<filename>"""
    user_id = instance.user.id
    return f'notes/user_{user_id}/{filename}'


class Note(models.Model):
    """Text note in markdown syntax"""
    title = models.CharField(
        max_length=100,
        verbose_name=_("title"),
        help_text="Note's title.")
    location = models.CharField(
        max_length=500,
        default="",
        blank=True,
        verbose_name=_("location"),
        help_text="Note's location in path-like format (eg.: random/stuff)")
    text = MarkdownxField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name=_("created by"),
        help_text="Identifies who created the note.")
    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True)
    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True)

    class Meta:
        verbose_name = _("note")
        verbose_name_plural = _("notes")
        unique_together = ('title', 'location', 'created_by')

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        self.location = '/'.join(map(lambda s: s.strip(), self.location.strip("/").split("/")))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('notes:note_edit', args=[str(self.id)])

    @property
    def full_path(self):
        """Get notes' full path"""
        if self.location == '':
            return f'{self.id}:{self.title}'
        return f'{self.location}/{self.id}:{self.title}'


class Tag(models.Model):
    """Generic tag"""
    name = models.CharField(
        max_length=100,
        verbose_name=_("name"),
        help_text="Tag's name.")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name=_("created by"),
        related_name="note_tags",
        help_text="Identifies who created the tag.")
    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True)
    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True)

    def __str__(self) -> str:
        return self.name

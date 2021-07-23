from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from markdownx.models import MarkdownxField

User = get_user_model()


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'notes/user_{0}/{1}'.format(instance.user.id, filename)


class Note(models.Model):
    title = models.CharField(
        max_length=200,
        help_text="Note's title.")
    location = models.CharField(
        max_length=2000,
        default="",
        blank=True,
        help_text="Note's location in format of a path of folders separated by '/'")
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

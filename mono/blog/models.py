from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from tinymce.models import HTMLField

User = get_user_model()


class Post(models.Model):
    title = models.CharField(_("title"), max_length=100)
    content = HTMLField(_("content"))
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("author"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name=_("post"))
    description = models.TextField(_("description"), max_length=1000)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("author"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

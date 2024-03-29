# Generated by Django 4.2.5 on 2023-09-20 19:22

import django.db.models.deletion
import markdownx.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Tag's name.",
                        max_length=100,
                        verbose_name="name",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="created at"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="updated at"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        help_text="Identifies who created the tag.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="note_tags",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="created by",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Note",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="Note's title.",
                        max_length=100,
                        verbose_name="title",
                    ),
                ),
                (
                    "location",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Note's location in path-like format (eg.: random/stuff)",
                        max_length=500,
                        verbose_name="location",
                    ),
                ),
                ("text", markdownx.models.MarkdownxField()),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="created at"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="updated at"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        help_text="Identifies who created the note.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="created by",
                    ),
                ),
            ],
            options={
                "verbose_name": "note",
                "verbose_name_plural": "notes",
                "ordering": ("location", "title"),
                "unique_together": {("title", "location", "created_by")},
            },
        ),
    ]

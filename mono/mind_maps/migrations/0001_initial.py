# Generated by Django 4.2.5 on 2023-09-20 19:22

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MindMap",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("scale", models.FloatField(default=10)),
                ("color", models.CharField(default="#0F0F0F", max_length=7)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Node",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("x", models.FloatField(default=120.0)),
                ("y", models.FloatField(default=120.0)),
                ("font_size", models.FloatField(default=1)),
                ("padding", models.FloatField(default=1)),
                ("border_size", models.FloatField(default=0.3)),
                (
                    "font_color",
                    models.CharField(default="#E0E1E2", max_length=7),
                ),
                (
                    "border_color",
                    models.CharField(default="#888888", max_length=7),
                ),
                (
                    "background_color",
                    models.CharField(default="#303030", max_length=7),
                ),
                ("bold", models.BooleanField(default=False)),
                ("italic", models.BooleanField(default=False)),
                ("underline", models.BooleanField(default=False)),
                ("line_through", models.BooleanField(default=False)),
                ("collapsed", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "mind_map",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mind_maps.mindmap",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="mind_maps.node",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]

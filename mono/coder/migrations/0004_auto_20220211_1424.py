# Generated by Django 3.2.12 on 2022-02-11 14:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("coder", "0003_auto_20220210_1425"),
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
                    "order",
                    models.PositiveIntegerField(
                        db_index=True, editable=False, verbose_name="order"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(blank=True, default="", max_length=100),
                ),
                (
                    "color",
                    models.CharField(
                        choices=[
                            ("rd", "Red"),
                            ("org", "Orange"),
                            ("ylw", "Yellow"),
                            ("olv", "Olive"),
                            ("grn", "Green"),
                            ("tl", "Teal"),
                            ("blu", "Blue"),
                            ("vlt", "Violet"),
                            ("prp", "Purple"),
                            ("pnk", "Pink"),
                            ("brn", "Brown"),
                            ("gry", "Grey"),
                            ("blk", "Black"),
                        ],
                        default="blu",
                        max_length=100,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="coder_tags",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="snippet",
            name="tags",
            field=models.ManyToManyField(blank=True, null=True, to="coder.Tag"),
        ),
    ]

# Generated by Django 3.2.12 on 2022-02-20 21:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("curriculum_builder", "0004_auto_20220209_0102"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="curriculum",
            name="companies",
        ),
        migrations.AddField(
            model_name="company",
            name="curriculum",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="curriculum_builder.curriculum",
            ),
            preserve_default=False,
        ),
    ]

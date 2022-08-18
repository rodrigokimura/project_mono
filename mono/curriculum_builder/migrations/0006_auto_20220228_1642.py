# Generated by Django 3.2.12 on 2022-02-28 19:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("curriculum_builder", "0005_auto_20220220_1839"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="curriculum",
            name="skills",
        ),
        migrations.RemoveField(
            model_name="curriculum",
            name="social_media_profiles",
        ),
        migrations.AddField(
            model_name="skill",
            name="curriculum",
            field=models.ForeignKey(
                default=2,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="skills",
                to="curriculum_builder.curriculum",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="socialmediaprofile",
            name="curriculum",
            field=models.ForeignKey(
                default=2,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="social_media_profiles",
                to="curriculum_builder.curriculum",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="company",
            name="curriculum",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="companies",
                to="curriculum_builder.curriculum",
            ),
        ),
    ]

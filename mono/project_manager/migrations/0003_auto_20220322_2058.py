# Generated by Django 3.2.12 on 2022-03-22 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project_manager", "0002_auto_20220125_1646"),
    ]

    operations = [
        migrations.AddField(
            model_name="board",
            name="order",
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name="project",
            name="order",
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="board",
            name="tags_feature",
            field=models.BooleanField(
                default=True, help_text="Enables tags on cards"
            ),
        ),
    ]

# Generated by Django 3.2.12 on 2022-04-02 00:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("project_manager", "0003_auto_20220322_2058"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="board",
            options={"ordering": ["project", "order", "created_at"]},
        ),
    ]

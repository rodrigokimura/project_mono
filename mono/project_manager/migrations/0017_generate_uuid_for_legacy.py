# Generated by Django 3.2.13 on 2022-07-05 02:04

import uuid

from django.db import migrations


def gen_uuid(apps, schema_editor):
    models = [
        "board",
        "bucket",
        "card",
        "cardfile",
        "comment",
        "icon",
        "invite",
        "item",
        "project",
        "space",
        "tag",
        "theme",
        "timeentry",
    ]
    for model in models:
        Model = apps.get_model("project_manager", model)
        for row in Model.objects.all():
            row.public_id = uuid.uuid4()
            row.save(update_fields=["public_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("project_manager", "0016_add_uuid_fields"),
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]

# Generated by Django 4.1.2 on 2022-11-01 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mind_maps", "0011_mindmap_color"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mindmap",
            name="color",
            field=models.CharField(default="#0F0F0F", max_length=7),
        ),
        migrations.AlterField(
            model_name="node",
            name="background_color",
            field=models.CharField(default="#303030", max_length=7),
        ),
        migrations.AlterField(
            model_name="node",
            name="border_color",
            field=models.CharField(default="#888888", max_length=7),
        ),
        migrations.AlterField(
            model_name="node",
            name="font_color",
            field=models.CharField(default="#E0E1E2", max_length=7),
        ),
    ]
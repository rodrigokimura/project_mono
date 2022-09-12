# Generated by Django 4.1 on 2022-09-12 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "mind_maps",
            "0008_alter_node_font_size_alter_node_padding_alter_node_x_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="node",
            name="background_color",
            field=models.CharField(default="#ffffff", max_length=7),
        ),
        migrations.AddField(
            model_name="node",
            name="border_color",
            field=models.CharField(default="#ffffff", max_length=7),
        ),
        migrations.AddField(
            model_name="node",
            name="border_size",
            field=models.FloatField(default=0.3),
        ),
        migrations.AddField(
            model_name="node",
            name="font_color",
            field=models.CharField(default="#000000", max_length=7),
        ),
    ]

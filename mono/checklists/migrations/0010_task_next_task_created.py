# Generated by Django 3.2.13 on 2022-05-26 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0009_alter_task_due_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='next_task_created',
            field=models.BooleanField(default=False),
        ),
    ]

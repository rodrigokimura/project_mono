# Generated by Django 3.2.13 on 2022-05-26 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0007_configuration'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='recurrence',
            field=models.CharField(blank=True, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], max_length=7, null=True),
        ),
    ]

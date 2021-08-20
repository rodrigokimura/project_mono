# Generated by Django 3.2.4 on 2021-08-18 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0042_alter_card_tag'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(fields=('board', 'name'), name='unique_tag'),
        ),
    ]
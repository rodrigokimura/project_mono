# Generated by Django 3.2.5 on 2021-08-07 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0026_invite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invite',
            name='email',
            field=models.EmailField(blank=True, max_length=1000, null=True),
        ),
    ]
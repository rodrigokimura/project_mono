# Generated by Django 3.2.11 on 2022-01-20 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0065_alter_chart_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plan',
            name='icon',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='plan',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='user',
        ),
        migrations.DeleteModel(
            name='Feature',
        ),
        migrations.DeleteModel(
            name='Plan',
        ),
        migrations.DeleteModel(
            name='Subscription',
        ),
    ]
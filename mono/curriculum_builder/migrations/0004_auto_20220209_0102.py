# Generated by Django 3.2.12 on 2022-02-09 04:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum_builder', '0003_alter_acomplishment_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='curriculum',
            name='work_experiences',
        ),
        migrations.AddField(
            model_name='curriculum',
            name='companies',
            field=models.ManyToManyField(to='curriculum_builder.Company'),
        ),
        migrations.AlterField(
            model_name='acomplishment',
            name='work_experience',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='acomplishments', to='curriculum_builder.workexperience'),
        ),
        migrations.AlterField(
            model_name='workexperience',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_experiences', to='curriculum_builder.company'),
        ),
    ]
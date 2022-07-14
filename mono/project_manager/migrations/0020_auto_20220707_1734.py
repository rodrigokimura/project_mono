# Generated by Django 3.2.13 on 2022-07-07 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0019_auto_20220705_2116'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'verbose_name': 'activity', 'verbose_name_plural': 'activities'},
        ),
        migrations.AlterField(
            model_name='activity',
            name='action',
            field=models.CharField(choices=[('create_card', '%(user)s created card'), ('update_name', '%(user)s updated card name from %(old)s to %(new)s'), ('update_description', '%(user)s updated card description'), ('update_due_date', '%(user)s updated card due date from %(old)s to %(new)s'), ('update_status', '%(user)s updated card status from %(old)s to %(new)s'), ('update_color', '%(user)s updated card color from %(old)s to %(new)s'), ('add_tags', '%(user)s added tag %(tag)s'), ('remove_tags', '%(user)s removed tag %(tag)s'), ('add_assigned_user', '%(user)s assigned %(assignee)s to card'), ('remove_assigned_user', "%(user)s removed %(assignee)s from card's assigned users"), ('add_checklist_item', '%(user)s added checklist item %(item)s'), ('update_checklist_item', '%(user)s updated checklist item from %(old)s to %(new)s'), ('remove_checklist_item', '%(user)s removed checklist item %(item)s'), ('add_comment', '%(user)s added comment'), ('update_comment', '%(user)s updated comment'), ('remove_comment', '%(user)s removed comment'), ('add_file', '%(user)s added a file'), ('remove_file', '%(user)s removed a file'), ('start_timer', '%(user)s started timer'), ('stop_timer', '%(user)s stopped timer (logged duration: %(duration)s)'), ('update_time_entry', '%(user)s updated a time entry (duration changed from %(old)s to %(new)s)'), ('delete_time_entry', '%(user)s deleted a time entry')], max_length=100),
        ),
    ]
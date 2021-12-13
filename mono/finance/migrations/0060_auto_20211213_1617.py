# Generated by Django 3.2.10 on 2021-12-13 16:17

import django.db.models.deletion
import django.utils.timezone
import multiselectfield.db.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0059_chart_filters'),
    ]

    operations = [
        migrations.AddField(
            model_name='chart',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='chart',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='charts', to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='chart',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='chart',
            name='filters',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('none', 'None'), ('expenses', 'Expenses'), ('incomes', 'Incomes'), ('balance_adjustments', 'Balance adjustments'), ('not_balance_adjustments', 'Not balance adjustments'), ('transferences', 'Transferences'), ('not_transferences', 'Not transferences'), ('current_year', 'Current year'), ('past_year', 'Past year'), ('current_month', 'Current month'), ('past_month', 'Past month')], default=None, max_length=145, null=True),
        ),
    ]

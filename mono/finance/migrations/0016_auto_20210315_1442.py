# Generated by Django 3.1.7 on 2021-03-15 17:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0015_auto_20210313_2257'),
    ]

    operations = [
        migrations.RenameField(
            model_name='budget',
            old_name='goal',
            new_name='ammount',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='period',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='status',
        ),
        migrations.AddField(
            model_name='budget',
            name='end_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='budget',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.CreateModel(
            name='BudgetConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ammount', models.FloatField()),
                ('frequency', models.CharField(choices=[('W', 'Weekly'), ('M', 'Monthly'), ('Y', 'Yearly')], default='M', max_length=1)),
                ('active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='budget',
            name='configuration',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='finance.budgetconfiguration'),
        ),
    ]

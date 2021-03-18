# Generated by Django 3.1.7 on 2021-03-18 14:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0018_budget_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='ammount',
            field=models.FloatField(help_text='Ammount related to the transaction. Absolute value, no positive/negative signs.'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='created_by',
            field=models.ForeignKey(help_text='Identifies how created the transaction.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='description',
            field=models.CharField(help_text='A short description, so that the user can identify the transaction.', max_length=50),
        ),
    ]

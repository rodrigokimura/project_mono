# Generated by Django 3.1.7 on 2021-03-29 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0030_budgetconfiguration_data_squashed_0032_auto_20210329_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budgetconfiguration',
            name='start_date',
            field=models.IntegerField(),
        ),
    ]

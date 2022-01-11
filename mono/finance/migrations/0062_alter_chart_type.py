# Generated by Django 3.2.10 on 2021-12-14 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0061_auto_20211213_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chart',
            name='type',
            field=models.CharField(choices=[('bar', 'Bar'), ('line', 'Line'), ('column', 'Column'), ('donut', 'Donut')], default='bar', max_length=100),
        ),
    ]
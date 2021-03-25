# Generated by Django 3.1.7 on 2021-03-25 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0021_auto_20210323_1755'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(help_text='Stores the stripe unique identifiers', max_length=100)),
                ('name', models.CharField(help_text='Display name used on the template', max_length=100)),
                ('description', models.TextField(help_text='Description text used on the template', max_length=500)),
                ('type', models.CharField(choices=[('FR', 'Free'), ('LT', 'Lifetime'), ('DF', 'Default'), ('RC', 'Recommended')], help_text='Used to customize the template based on this field. For instance, the basic plan will be muted and the recommended one is highlighted.', max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_description', models.CharField(max_length=30)),
                ('full_description', models.TextField(max_length=100)),
                ('internal_description', models.TextField(blank=True, default=None, help_text='This is used by staff and is not displayed to user in the template.', max_length=1000, null=True)),
                ('display', models.BooleanField(default=True, help_text='Controls wether feature is shown on the template')),
                ('icon', models.ForeignKey(blank=True, default=None, help_text='Icon rendered in the template', null=True, on_delete=django.db.models.deletion.SET_NULL, to='finance.icon')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.plan')),
            ],
        ),
    ]

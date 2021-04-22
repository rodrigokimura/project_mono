# Generated by Django 3.2 on 2021-04-22 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0043_auto_20210414_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installment',
            name='handle_remainder',
            field=models.CharField(choices=[('F', 'Add to first transaction'), ('L', 'Add to last transaction')], default='F', max_length=1, verbose_name='handle remainder'),
        ),
        migrations.AlterField(
            model_name='installment',
            name='months',
            field=models.IntegerField(default=12, verbose_name='months'),
        ),
        migrations.AlterField(
            model_name='recurrenttransaction',
            name='frequency',
            field=models.CharField(choices=[('W', 'Weekly'), ('M', 'Monthly'), ('Y', 'Yearly')], default='M', max_length=1, verbose_name='frequency'),
        ),
    ]

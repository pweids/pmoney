# Generated by Django 2.0 on 2018-01-06 03:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0003_auto_20171230_0411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lineitem',
            name='credit_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='debit_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
    ]

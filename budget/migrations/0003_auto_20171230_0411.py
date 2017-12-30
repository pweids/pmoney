# Generated by Django 2.0 on 2017-12-30 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0002_lineitem_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lineitem',
            name='credit_amount',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='debit_amount',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
    ]
# Generated by Django 2.2 on 2020-12-26 14:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pet', '0006_auto_20201222_1242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersubscribed',
            name='subscribed_expiry',
            field=models.DateField(default=datetime.date(2021, 12, 26)),
        ),
    ]

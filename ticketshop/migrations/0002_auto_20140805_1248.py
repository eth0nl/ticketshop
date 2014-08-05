# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticketshop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='bar_credits',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='donation',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, 'waiting for payment'), (1, 'paid'), (2, 'cancelled'), (3, 'used')]),
        ),
    ]

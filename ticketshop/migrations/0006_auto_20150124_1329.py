# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticketshop', '0005_auto_20150124_1329'),
    ]

    operations = [
        migrations.AddField(
            model_name='tickettype',
            name='max_tickets',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tickettype',
            name='sold_out',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

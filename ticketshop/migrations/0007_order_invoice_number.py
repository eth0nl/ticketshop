# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticketshop', '0006_auto_20150124_1329'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='invoice_number',
            field=models.PositiveIntegerField(unique=True, null=True, blank=True),
            preserve_default=True,
        ),
    ]

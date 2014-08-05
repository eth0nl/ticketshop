# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ticketshop.models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketshop', '0003_auto_20140805_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='api_key',
            field=models.CharField(default=ticketshop.models.generate_random_code_16, max_length=20),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='admitted_timestamp',
            field=models.DateTimeField(null=True, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='barcode',
            field=models.ImageField(upload_to='barcode', editable=False),
        ),
    ]

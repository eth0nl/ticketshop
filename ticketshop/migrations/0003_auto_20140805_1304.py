# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ticketshop.models


def set_random_code(apps, schema_editor):
    Order = apps.get_model("ticketshop", "Order")
    for order in Order.objects.all():
        order.code = ticketshop.models.generate_random_code()
        order.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ticketshop', '0002_auto_20140805_1248'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='barcode',
            field=models.ImageField(default='', upload_to=b'', editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='code',
            field=models.CharField(default=ticketshop.models.generate_random_code, max_length=10),
            preserve_default=True,
        ),
        migrations.RunPython(set_random_code),
    ]

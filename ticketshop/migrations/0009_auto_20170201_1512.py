# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketshop', '0008_auto_20160118_2244'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='tickettype',
            options={'ordering': ['event', 'price']},
        ),
        migrations.AlterField(
            model_name='tickettype',
            name='description',
            field=models.CharField(max_length=150),
        ),
    ]

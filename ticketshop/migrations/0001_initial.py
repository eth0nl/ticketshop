# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django.core.validators


def create_active_event(apps, schema_editor):
    ActiveEvent = apps.get_model("ticketshop", "ActiveEvent")
    ActiveEvent.objects.create()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('organisation', models.CharField(max_length=100, blank=True)),
                ('address', models.CharField(max_length=64, blank=True)),
                ('zip_code', models.CharField(max_length=7, blank=True)),
                ('city', models.CharField(max_length=64, blank=True)),
                ('country', models.CharField(max_length=64, blank=True)),
                ('groups', models.ManyToManyField(to='auth.Group', verbose_name='groups', blank=True)),
                ('user_permissions', models.ManyToManyField(to='auth.Permission', verbose_name='user permissions', blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActiveEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('location', models.CharField(max_length=100)),
                ('url', models.URLField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='activeevent',
            name='event',
            field=models.ForeignKey(blank=True, to='ticketshop.Event', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('bar_credits', models.PositiveIntegerField()),
                ('donation', models.PositiveIntegerField()),
                ('payment_id', models.CharField(max_length=30, blank=True)),
                ('status', models.IntegerField(choices=[(0, 'waiting for payment'), (1, 'paid'), (2, 'cancelled'), (3, 'used')])),
                ('event', models.ForeignKey(to='ticketshop.Event')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.PositiveIntegerField()),
                ('order', models.ForeignKey(to='ticketshop.Order')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TicketType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=70)),
                ('description', models.CharField(max_length=70)),
                ('price', models.PositiveIntegerField()),
                ('event', models.ForeignKey(to='ticketshop.Event')),
            ],
            options={
                'ordering': ['event', '-price'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ticket',
            name='type',
            field=models.ForeignKey(to='ticketshop.TicketType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='tickets',
            field=models.ManyToManyField(to='ticketshop.TicketType', through='ticketshop.Ticket', blank=True),
            preserve_default=True,
        ),
        migrations.RunPython(create_active_event),
    ]

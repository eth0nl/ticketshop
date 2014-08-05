# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property

from solo.models import SingletonModel


class User(AbstractUser):
    organisation = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=64, blank=True)
    zip_code = models.CharField(max_length=7, blank=True)
    city = models.CharField(max_length=64, blank=True)
    country = models.CharField(max_length=64, blank=True)


@python_2_unicode_compatible
class ActiveEvent(SingletonModel):
    event = models.ForeignKey('Event', null=True, blank=True)

    def __str__(self):
        if self.event:
            return self.event.name
        else:
            return "No active event"


@python_2_unicode_compatible
class Event(models.Model):
    name = models.CharField(max_length=50, unique=True)
    start = models.DateField()
    end = models.DateField()
    location = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class TicketType(models.Model):
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=70)
    event = models.ForeignKey('Event')
    price = models.PositiveIntegerField()

    class Meta:
        ordering = ['event', '-price']

    def __str__(self):
        return "%s %s" % (self.name, self.event)


@python_2_unicode_compatible
class Ticket(models.Model):
    type = models.ForeignKey('TicketType')
    order = models.ForeignKey('Order')
    count = models.PositiveIntegerField()

    def __str__(self):
        return "%dx %s" % (self.count, self.type)


email_body = """Hello,

Your payment of € {amount} for your {name} ticket(s) has been
received. We will send you the ticket(s) a few days before the event.

See you at {name}!

The {name} team
"""


@python_2_unicode_compatible
class Order(models.Model):
    PENDING, PAID, CANCELLED, USED = range(4)
    STATUS_CHOICES = (
        (PENDING, 'waiting for payment'),
        (PAID, 'paid'),
        (CANCELLED, 'cancelled'),
        (USED, 'used'),
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('User')
    event = models.ForeignKey('Event')
    tickets = models.ManyToManyField('TicketType', through='Ticket', blank=True)
    bar_credits = models.PositiveIntegerField(default=0)
    donation = models.PositiveIntegerField(default=0)
    payment_id = models.CharField(max_length=30, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return "Order %s" % self.id

    @cached_property
    def amount(self):
        total = 0
        for ticket in Ticket.objects.filter(order=self):
            total += ticket.count * ticket.type.price

        total += self.bar_credits
        total += self.donation

        return total

    @models.permalink
    def get_absolute_url(self):
        return ('order_detail', [self.id])

    def check_payment_status(self, payment):
        if payment['status'] == 'paid':
            self.status = self.PAID
            self.save()
            subject = 'Your {} payment was received'.format(self.event.name)
            send_mail(subject, email_body.format(name=self.event.name, amount=self.amount),
                      "tickets@eth0.nl", [self.user.email])
        elif payment['status'] == 'cancelled' or payment['status'] == 'expired':
            self.status = self.CANCELLED
            self.save()

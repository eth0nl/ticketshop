# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import EmailMessage
from django.db import models
from django.db.models import Max
from django.template.loader import render_to_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property

import os
import random
import string

from solo.models import SingletonModel
import weasyprint

from .code128 import Code128
from .bci import BarcodeImage


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


def generate_random_code_16():
    return ''.join(random.sample(string.ascii_letters + string.digits, 16))


@python_2_unicode_compatible
class Event(models.Model):
    name = models.CharField(max_length=50, unique=True)
    start = models.DateField()
    end = models.DateField()
    location = models.CharField(max_length=100)
    url = models.URLField()
    api_key = models.CharField(max_length=20, default=generate_random_code_16)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class TicketType(models.Model):
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=70)
    event = models.ForeignKey('Event')
    price = models.PositiveIntegerField()
    max_tickets = models.PositiveIntegerField(blank=True, null=True)
    sold_out = models.BooleanField(default=False)

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
received. The PDF of your ticket is attached to this e-mail.

See you at {name}!

The {name} team
"""


def generate_random_code():
    return ''.join(random.sample(string.ascii_letters + string.digits, 7))


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
    code = models.CharField(max_length=10, default=generate_random_code)
    barcode = models.ImageField(upload_to="barcode", editable=False)
    admitted_timestamp = models.DateTimeField(blank=True, null=True, editable=False)
    invoice_number = models.PositiveIntegerField(blank=True, null=True, unique=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return "Order %s" % self.id

    def save(self, *args, **kwargs):
        if not self.barcode:
            font = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono-Bold.ttf"
            imager = BarcodeImage(Code128(), font_file=font, font_size=20,
                                  barwidth=2, dpi=192, height=65)
            directory = os.path.join(settings.MEDIA_ROOT, 'barcode')
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename = os.path.join(directory, self.code + '.png')
            imager(self.code, self.code, output=filename)
            self.barcode.name = os.path.join('barcode', self.code + '.png')
        super(Order, self).save(*args, **kwargs)

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

    @models.permalink
    def get_pdf_url(self):
        return ('order_pdf', [self.id])

    def check_payment_status(self, payment):
        if payment['status'] == 'paid':
            self.status = self.PAID
            max_invoice_number = Order.objects.select_for_update().aggregate(Max('invoice_number'))['invoice_number__max']
            if max_invoice_number:
                self.invoice_number = max_invoice_number + 1
            else:
                self.invoice_number = 1
            self.save()
            self.send_ticket()
        elif payment['status'] == 'cancelled' or payment['status'] == 'expired':
            self.status = self.CANCELLED
            self.save()

    def send_ticket(self):
        subject = 'Your {} ticket(s)'.format(self.event.name)
        body = email_body.format(name=self.event.name, amount=self.amount)
        email = EmailMessage(subject, body, "tickets@eth0.nl", [self.user.email])
        tickets = []
        for ticket in Ticket.objects.filter(order=self):
            tickets.append({'count': ticket.count, 'name': ticket.type.name, 'price': ticket.type.price, 'total': ticket.count * ticket.type.price})
        html = render_to_string('ticketshop/order_pdf.html', {'order': self, 'tickets': tickets})
        pdf = weasyprint.HTML(string=html, base_url=settings.WEASYPRINT_BASEURL).write_pdf()
        email.attach(self.filename, pdf, 'application/pdf')
        email.send()

    @property
    def filename(self):
        return "ticket_%d.pdf" % self.id

    @property
    def invoice_filename(self):
        return "invoice_%d.pdf" % self.invoice_number

    @property
    def valid(self):
        if self.status in (self.PAID, self.USED):
            return True
        else:
            return False

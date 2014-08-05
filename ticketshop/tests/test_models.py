from __future__ import absolute_import, division, print_function, unicode_literals

from django.test import TestCase

from datetime import date

from ..models import Event, Order, Ticket, TicketType, User


class ModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.event = Event.objects.create(name='Test Event', location='test', start=date(2014, 1, 1), end=date(2014, 1, 5), url="http://www.example.org")
        self.tickettype1 = TicketType.objects.create(name="Test Ticket 17", description="test", event=self.event, price=17)
        self.tickettype2 = TicketType.objects.create(name="Test Ticket 7", description="test", event=self.event, price=7)

    def test_order(self):
        order = Order.objects.create(user=self.user, event=self.event)
        self.assertEqual(order.amount, 0)

        order = Order(user=self.user, event=self.event)
        order.donation = 5
        order.bar_credits = 10
        self.assertEqual(order.amount, 15)

        order = Order(user=self.user, event=self.event)
        order.donation = 5
        order.bar_credits = 10
        order.save()
        Ticket.objects.create(order=order, type=self.tickettype1, count=3)
        Ticket.objects.create(order=order, type=self.tickettype2, count=2)
        self.assertEqual(order.amount, 80)

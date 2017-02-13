from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib import admin
from django.db.models import Sum
from django.shortcuts import render_to_response
from django.template import RequestContext

from solo.admin import SingletonModelAdmin
from adminplus.sites import AdminSitePlus

from .models import ActiveEvent, Event, Order, Ticket, TicketType, User

admin.site = AdminSitePlus()


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'id', 'invoice_number', 'event', 'user', 'status', 'bar_credits', 'donation', 'amount')
    list_filter = ('event', 'status')
    inlines = (TicketInline,)
    readonly_fields = ('admitted_timestamp',)


class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price')


@admin.site.register_view('stats', 'Statistics')
def stats(request):
    event = ActiveEvent.objects.get().event
    context = {}
    context['title'] = event.name + ' statistics'
    context['tickets'] = []
    context['total'] = 0
    context['total_paid'] = 0
    context['subtotal_count'] = 0
    context['subtotal_count_paid'] = 0
    for ticket in TicketType.objects.filter(event=event):
        count = Ticket.objects.filter(order__event=event, order__status__in=(Order.PAID, Order.USED, Order.PENDING), type=ticket).aggregate(count=Sum('count'))['count']
        count_paid = Ticket.objects.filter(order__event=event, order__status__in=(Order.PAID, Order.USED), type=ticket).aggregate(count=Sum('count'))['count'] or 0
        if count:
            context['tickets'].append({'count': count, 'total': count * ticket.price, 'name': ticket.name, 'price': ticket.price,
                                       'count_paid': count_paid, 'total_paid': count_paid * ticket.price})
            context['total'] += count * ticket.price
            context['subtotal_count'] += count
            context['total_paid'] += count_paid * ticket.price
            context['subtotal_count_paid'] += count_paid

    context['subtotal_tickets'] = context['total']
    context['subtotal_tickets_paid'] = context['total_paid']
    context['bar_credits'] = Order.objects.filter(event=event, status__in=(Order.PAID, Order.USED, Order.PENDING)).aggregate(bar_credits=Sum('bar_credits'))['bar_credits']
    context['bar_credits_paid'] = Order.objects.filter(event=event, status__in=(Order.PAID, Order.USED)).aggregate(bar_credits=Sum('bar_credits'))['bar_credits']
    context['donation'] = Order.objects.filter(event=event, status__in=(Order.PAID, Order.USED, Order.PENDING)).aggregate(donation=Sum('donation'))['donation']
    context['donation_paid'] = Order.objects.filter(event=event, status__in=(Order.PAID, Order.USED)).aggregate(donation=Sum('donation'))['donation']
    if context['bar_credits']:
        context['total'] += context['bar_credits']
    if context['bar_credits_paid']:
        context['total_paid'] += context['bar_credits_paid']
    if context['donation']:
        context['total'] += context['donation']
    if context['donation_paid']:
        context['total_paid'] += context['donation_paid']

    return render_to_response('ticketshop/admin/stats.html',
                              context,
                              RequestContext(request, {}))


admin.site.register(ActiveEvent, SingletonModelAdmin)
admin.site.register(Event)
admin.site.register(Order, OrderAdmin)
admin.site.register(Ticket)
admin.site.register(TicketType, TicketTypeAdmin)
admin.site.register(User)

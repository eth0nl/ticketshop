from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib import admin

from solo.admin import SingletonModelAdmin

from .models import ActiveEvent, Event, Order, Ticket, TicketType, User


class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price')


admin.site.register(ActiveEvent, SingletonModelAdmin)
admin.site.register(Event)
admin.site.register(Order)
admin.site.register(Ticket)
admin.site.register(TicketType, TicketTypeAdmin)
admin.site.register(User)

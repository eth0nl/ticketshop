from __future__ import absolute_import, division, print_function, unicode_literals

from django import forms
from django.core.exceptions import SuspiciousOperation


class OrderForm(forms.Form):
    bar_credits = forms.TypedChoiceField(choices=((i, i) for i in range(6)), coerce=int, empty_value=0)
    donation = forms.IntegerField(initial=0, min_value=0, required=False)
    conditions = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        self.sold_out_tickets = set()
        tickets = kwargs.pop('tickets')
        super(OrderForm, self).__init__(*args, **kwargs)
        for ticket in tickets:
            ticket_field_name = 'ticket_%d' % ticket.id
            field = forms.TypedChoiceField(choices=((i, i) for i in range(6)), coerce=int, empty_value=0, required=(not ticket.sold_out))
            if ticket.sold_out:
                field.widget.attrs['disabled'] = 'disabled'
                self.sold_out_tickets.add(ticket_field_name)
            field.ticket = ticket
            self.fields[ticket_field_name] = field

    def clean_donation(self):
        # Not filling in anything should be treated the same as zero.
        donation = self.cleaned_data['donation']
        if not donation:
            return 0
        else:
            return donation

    def ticket_fields(self):
        for name in self.fields:
            if name.startswith('ticket_'):
                yield self[name]

    def clean(self):
        cleaned_data = super(OrderForm, self).clean()
        total = 0
        for k, v in cleaned_data.items():
            if k in self.sold_out_tickets and v != 0:
                raise SuspiciousOperation("Sold out ticket selected")
            if k != 'conditions':
                total += v
        if not total:
            raise forms.ValidationError("You have not selected anything!")


class ConfirmForm(forms.Form):
    pass

 # -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.utils.timezone import now
from django.views.generic import DetailView, FormView, TemplateView, View

from django_downloadview import ObjectDownloadView
from django_weasyprint import PDFTemplateResponseMixin
import Mollie

from .forms import ConfirmForm, OrderForm
from .models import ActiveEvent, Order, Ticket, TicketType


mollie = Mollie.API.Client()
mollie.setApiKey(settings.MOLLIE_API_KEY)


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class HomeView(FormView):
    template_name = "ticketshop/home.html"
    form_class = OrderForm
    success_url = "/confirm/"

    def __init__(self, *args, **kwargs):
        super(HomeView, self).__init__(*args, **kwargs)
        self.event = ActiveEvent.objects.get().event
        self.tickets = TicketType.objects.filter(event=self.event)

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            context['orders'] = Order.objects.filter(user=self.request.user)
        return context

    def get_form_kwargs(self):
        kwargs = super(HomeView, self).get_form_kwargs()
        kwargs['tickets'] = self.tickets
        return kwargs

    def form_valid(self, form):
        self.request.session['order'] = form.cleaned_data
        return super(HomeView, self).form_valid(form)


class TermsView(TemplateView):
    template_name = "ticketshop/terms.html"

    def get_context_data(self, **kwargs):
        context = super(TermsView, self).get_context_data(**kwargs)
        context['event'] = ActiveEvent.objects.get().event
        return context


class ConfirmView(LoginRequiredMixin, FormView):
    template_name = "ticketshop/confirm.html"
    form_class = ConfirmForm

    def __init__(self, *args, **kwargs):
        super(ConfirmView, self).__init__(*args, **kwargs)
        self.event = ActiveEvent.objects.get().event
        self.tickets = TicketType.objects.filter(event=self.event).select_for_update()

    def get_context_data(self, **kwargs):
        context = super(ConfirmView, self).get_context_data(**kwargs)
        total = 0
        order = self.request.session['order']
        tickets = []
        for ticket in self.tickets:
            count = order['ticket_%d' % ticket.id]
            if count:
                if ticket.max_tickets:
                    # FIXME: We should be able to do this with less queries
                    ticket_count = Ticket.objects.filter(order__event=self.event, type=ticket).exclude(order__status=Order.CANCELLED).aggregate(count=Sum('count'))['count']
                    if not ticket_count:
                        ticket_count = 0
                    if ticket_count + count > ticket.max_tickets:
                        # FIXME: We need to make sure the form doesn't show more tickets than there are available
                        raise Exception("Should not be possible to order more tickets than available")
                    else:
                        if ticket_count + count == ticket.max_tickets:
                            ticket.sold_out = True
                            ticket.save()
                tickets.append({'count': count, 'name': ticket.name, 'price': ticket.price, 'total': count * ticket.price})
                total += count * ticket.price
        context['tickets'] = tickets
        context['bar_credits'] = order['bar_credits'] * 10
        total += order['bar_credits'] * 10
        context['donation'] = order['donation']
        total += order['donation']
        context['total'] = total

        return context

    def form_valid(self, form):
        order_dict = self.request.session['order']
        order = Order(event=self.event, user=self.request.user, status=Order.PENDING)
        order.bar_credits = order_dict['bar_credits'] * 10
        order.donation = order_dict['donation']
        order.save()
        tickets = []
        amount = 0
        for tickettype in self.tickets:
            count = order_dict['ticket_%d' % tickettype.id]
            if count:
                tickets.append(Ticket.objects.create(order=order, type=tickettype, count=count))
                amount += count * tickettype.price

        amount += order.donation + order.bar_credits

        payment = mollie.payments.create({
            'amount': amount,
            'description': self.event.name,
            'redirectUrl': 'https://tickets.eth0.nl/order/%d/' % order.id
        })

        order.payment_id = payment['id']
        order.save()

        return HttpResponseRedirect(payment.getPaymentUrl())


class OrderBarCodeView(ObjectDownloadView):
    model = Order
    file_field = 'barcode'
    attachment = False
    mimetype = 'image/png'

    def get_queryset(self):
        qs = super(OrderBarCodeView, self).get_queryset()
        return qs.filter(user=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order

    def get_queryset(self):
        qs = super(OrderDetailView, self).get_queryset()
        return qs.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        total = 0
        tickets = []
        for ticket in Ticket.objects.filter(order=self.object):
            tickets.append({'count': ticket.count, 'name': ticket.type.name, 'price': ticket.type.price, 'total': ticket.count * ticket.type.price})
            total += ticket.count * ticket.type.price

        context['tickets'] = tickets

        return context


class OrderPdfView(OrderDetailView, PDFTemplateResponseMixin):
    template_name = "ticketshop/order_pdf.html"

    def get_queryset(self):
        qs = super(OrderPdfView, self).get_queryset()
        return qs.filter(user=self.request.user)

    def get_filename(self):
        return self.object.filename


class WebhookView(View):
    def post(self, request, *args, **kwargs):
        if 'testByMollie' in request.GET:
            return HttpResponse()
        payment = mollie.payments.get(request.POST['id'])
        order = Order.objects.get(payment_id=payment['id'])
        order.check_payment_status(payment)

        return HttpResponse()


class ProtectedApiView(View):
    def post(self, request, *args, **kwargs):
        event = ActiveEvent.objects.get().event
        if request.POST['api_key'] != event.api_key:
            return HttpResponseForbidden()

        return self.protected_post(request, *args, **kwargs)


class CheckTicketView(ProtectedApiView):
    def protected_post(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(code=request.POST['ticket_id'])
        except Order.DoesNotExist:
            return JsonResponse({'result': 'invalid'})

        if order.status == Order.PAID:
            response = {'result': 'valid', 'tickets': []}
            for ticket in Ticket.objects.filter(order=order):
                response['tickets'].append({'name': ticket.type.name, 'count': ticket.count})
            response['bar_credits'] = order.bar_credits
            response['username'] = order.user.username

            order.status = Order.USED
            order.admitted_timestamp = now()
            order.save()

            return JsonResponse(response)
        elif order.status == Order.USED:
            return JsonResponse({'result': 'used'})

        return JsonResponse({'result': 'invalid'})

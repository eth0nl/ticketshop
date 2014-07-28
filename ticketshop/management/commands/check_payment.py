from django.core.management.base import BaseCommand, CommandError

from ...models import Order
from ...views import mollie


class Command(BaseCommand):
    args = "order_id"
    help = "Check payment status of order"

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Need exactly one argument")

        order = Order.objects.get(id=int(args[0]))
        payment = mollie.payments.get(order.payment_id)
        order.check_payment_status(payment)

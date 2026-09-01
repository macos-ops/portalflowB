from django.core.management.base import BaseCommand
from django.utils import timezone
from invoices.models import Invoice


class Command(BaseCommand):
    help = "Marks all SENT invoices past their due_date as OVERDUE"

    def handle(self, *args, **options):
        today = timezone.now().date()

        overdue_invoices = Invoice.objects.filter(
            status=Invoice.Status.SENT,
            due_date__lt=today,
        )

        count = overdue_invoices.count()
        overdue_invoices.update(status=Invoice.Status.OVERDUE)

        self.stdout.write(
            self.style.SUCCESS(f"Marked {count} invoice(s) as OVERDUE.")
        )

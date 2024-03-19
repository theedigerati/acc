from django.db import models


class InvoiceManager(models.Manager):
    def active(self):
        return self.get_queryset().filter(archived=False)

    def active_not_draft(self):
        return self.get_queryset().filter(is_draft=False, archived=False)

    def get_outstanding(self):
        """
        Calculate total amount due for all active invoices.
        Amount due for invoices in draft are not added to "total".
        """
        draft, overdue, total = 0, 0, 0
        for invoice in (
            self.get_queryset()
            .filter(archived=False)
            .prefetch_related("lines", "payments")
        ):
            if invoice.is_draft:
                draft += invoice.amount_due
                continue
            if invoice.is_overdue:
                overdue += invoice.amount_due
            total += invoice.amount_due
        return {"draft": draft, "overdue": overdue, "total": total}


class PaymentReceivedManager(models.Manager):
    def create(self, **kwargs):
        instance = super().create(**kwargs)
        if instance.invoice.is_draft:
            instance.invoice.is_draft = False
            instance.invoice.save()
        return instance

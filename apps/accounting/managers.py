from datetime import datetime, timezone
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.db import transaction
from django.utils import timezone as django_timezone
from django.apps import apps
from django.conf import settings


class ActiveAccountManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)


class TransactionManager(models.Manager):
    """
    Custon manager methods to record & delete
    transactions from resources.

    Note: Debit transactions increase Asset & Expense accounts,
          decrease liability, equity & income accounts.

          Credit transactions decrease Asset & Expense accounts,
          increase liability, equity & income accounts.
    """

    def record_journal_entry(self, journal_entry):
        JournalEntry = apps.get_model("accounting.JournalEntry")
        assert isinstance(journal_entry, JournalEntry)
        transaction_data = {
            "date": journal_entry.date,
            "ref": journal_entry,
            "name": f"Journal Entry: {journal_entry.name}",
            "note": journal_entry.note,
            "transactions": [
                *[
                    {
                        "account_code": line.account.code,
                        "type": line.type,
                        "amount": line.amount,
                    }
                    for line in journal_entry.lines.select_related("account")
                ]
            ],
        }
        self._record_transaction(**transaction_data)

    def _record_transaction(self, **kwargs):
        account_model = self.model.account.field.related_model
        queryset = self.get_queryset()
        contenttype = ContentType.objects.get(
            app_label=kwargs["ref"]._meta.app_label,
            model=kwargs["ref"]._meta.model_name,
        )
        defaults = {
            "ref_type": contenttype,
            "ref_id": kwargs["ref"].id,
            "ref": kwargs["ref"],
            "date": datetime.combine(
                kwargs["date"],
                django_timezone.now().time(),
                timezone.utc if settings.USE_TZ else None,
            ),
            "name": kwargs["name"],
            "note": kwargs["note"],
        }

        with transaction.atomic():
            # delete existing records
            queryset.filter(ref_type=contenttype, ref_id=kwargs["ref"].id).delete()
            try:
                for record in kwargs["transactions"]:
                    _defaults = {
                        **defaults,
                        "name": (
                            record["name"] if "name" in record else defaults["name"]
                        ),
                    }
                    queryset.create(
                        account=account_model.actives.get(code=record["account_code"]),
                        type=record["type"],
                        amount=record["amount"],
                        **_defaults,
                    )
            except MultipleObjectsReturned:
                raise ValidationError(
                    "Multiple transactions/accounts found with the same reference."
                )
            except account_model.DoesNotExist:
                raise ValidationError("Account provided was not found or is archived.")

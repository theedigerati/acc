from django.db import models


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

    pass

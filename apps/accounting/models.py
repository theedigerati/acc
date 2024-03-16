from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from .managers import ActiveAccountManager, TransactionManager


class AccountType(models.TextChoices):
    ASSET = (
        "asset",
        "Asset",
    )
    LIABILITY = (
        "liability",
        "Liability",
    )
    EQUITY = (
        "equity",
        "Equity",
    )
    INCOME = (
        "inocome",
        "Income",
    )
    EXPENSE = "expense", "Expense"


class AccountSubType(models.Model):
    """
    Account subtypes give more specificity to account types.
    e.g Cash & Bank -> Asset, Current Liability -> Liability etc.
    """

    name = models.CharField(max_length=64, unique=True)
    type = models.CharField(max_length=10, choices=AccountType.choices)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.name


class Account(models.Model):
    """
    Financial Account for recording transactions.
    Each instance must be of one AccountSubType.
    """

    name = models.CharField(max_length=128, db_index=True)
    code = models.CharField(max_length=16, unique=True)
    description = models.TextField(blank=True)
    sub_type = models.ForeignKey(AccountSubType, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="sub_accounts",
    )
    is_archived = models.BooleanField(default=False)
    editable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    actives = ActiveAccountManager()

    class Meta:
        ordering = ["code", "created_at"]

    def __str__(self) -> str:
        return self.name

    @property
    def type(self) -> str:
        return self.sub_type.type

    @property
    def is_sub_account(self) -> bool:
        return bool(self.parent)

    @property
    def sibling_sub_types(self):
        """
        Account sub types with same type
        """

        return AccountSubType.objects.filter(type=self.type)

    @property
    def sibling_accounts(self):
        """
        Accounts with same sub types
        """
        return Account.objects.filter(sub_type=self.sub_type).exclude(id=self.id)


class TransactionType(models.TextChoices):
    DEBIT = (
        "debit",
        "Debit - Increase Assets & Expense, Decrease Equity, Liability & Income",
    )
    CREDIT = (
        "credit",
        "Credit - Decrease Assets & Expense, Increase Equity, Liability & Income",
    )


class Transaction(models.Model):
    # non-nullable reference for a transaction
    # (invoice | bill | expense | payments | journal entry)
    ref_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    ref_id = models.PositiveIntegerField()
    ref = GenericForeignKey("ref_type", "ref_id")

    name = models.CharField(max_length=50)
    note = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(
        "accounting.Account", related_name="transactions", on_delete=models.PROTECT
    )
    type = models.CharField(max_length=6, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    objects = TransactionManager()

    class Meta:
        indexes = [models.Index(fields=["ref_type", "ref_id", "date"])]
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.account}/{self.name} --> {self.amount}"

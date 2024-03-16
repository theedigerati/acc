from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from apps.accounting.models import (
    Account,
    AccountSubType,
)
from apps.accounting.serializers import (
    AccountSerializer,
    AccountSiblingsSerializer,
    AccountSubTypeSerializer,
    TransactionSerializer,
)


class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_serializer_class(self):
        if self.action == "siblings":
            return AccountSiblingsSerializer
        if self.action == "transactions":
            return TransactionSerializer
        return self.serializer_class

    @action(["get"], detail=True)
    def siblings(self, request, *args, **kwargs):
        # siblings data is generated in the serializer
        return self.retrieve(request, *args, **kwargs)

    @action(["get"], detail=True)
    def transactions(self, request, *args, **kwargs):
        insance = self.get_object()
        serializer = self.get_serializer(insance.transactions.all(), many=True)
        return Response(serializer.data)

    @action(["get"], detail=False)
    def subtypes(self, request, *args, **kwargs):
        serializer = AccountSubTypeSerializer(AccountSubType.objects.all(), many=True)
        return Response(serializer.data)

    @action(["get"], detail=False)
    def balance(self, request, *args, **kwargs):
        accounts = Account.actives.values(
            "id", bal=Sum("transactions__amount", default=0)
        )
        return Response(
            {
                account["id"]: account["bal"] if account["bal"] else 0
                for account in accounts
            }
        )

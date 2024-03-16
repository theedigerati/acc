from rest_framework import serializers
from apps.accounting.models import (
    Account,
    AccountSubType,
    Transaction,
)
from core.serializers.fields import PrimaryKey_To_ObjectField


class AccountSubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountSubType
        exclude = ("created_at",)


class AccountShallowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "name")


class AccountSerializer(serializers.ModelSerializer):
    sub_type = PrimaryKey_To_ObjectField(
        queryset=AccountSubType.objects.all(),
        object_serializer=AccountSubTypeSerializer,
    )

    class Meta:
        model = Account
        fields = (
            "id",
            "name",
            "code",
            "description",
            "sub_type",
            "parent",
            "is_archived",
            "editable",
        )

    def update(self, instance, validated_data):
        if not instance.editable:
            return serializers.ValidationError(
                "This account cannot be edited because it is used for automated transactions"
            )
        return super().update(instance, validated_data)


class AccountSiblingsSerializer(serializers.ModelSerializer):
    sub_types = AccountSubTypeSerializer(many=True, read_only=True)
    accounts = AccountSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ("sub_types", "accounts")

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["sub_types"] = AccountSubTypeSerializer(
            instance.sibling_sub_types, many=True
        ).data
        repr["accounts"] = AccountSerializer(instance.sibling_accounts, many=True).data
        return repr


class TransactionSerializer(serializers.ModelSerializer):
    account = serializers.SlugRelatedField(slug_field="name", read_only=True)
    ref_type = serializers.SlugRelatedField(slug_field="model", read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"

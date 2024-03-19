from rest_framework.serializers import ModelSerializer
from apps.address.models import Address


class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"

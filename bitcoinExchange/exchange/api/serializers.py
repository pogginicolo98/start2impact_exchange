from exchange.models import Order
from rest_framework import serializers


class OrderSerializer(serializers.ModelSerializer):
    """
    ModelSerializer for Order instances.

    fields
    - Profile
    - Price
    - Quantity
    - Type: False=sell, True=buy.
    - Created_at: Date format '31/12/2021, 23:59:59'.
    """

    profile = serializers.StringRelatedField(read_only=True)
    status = serializers.BooleanField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_created_at(self, instance):
        return instance.created_at.strftime("%d/%m/%Y, %H:%M:%S")

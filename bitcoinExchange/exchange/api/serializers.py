from django.shortcuts import get_object_or_404
from exchange.models import Order, Profile, Wallet
from rest_framework import serializers


class OrderSerializer(serializers.ModelSerializer):
    """
    ModelSerializer for Order instances.

    :fields
    - Profile
    - Price
    - Quantity
    - Type: Buy, Sell.
    - Created_at: Date format '31/12/2021, 23:59:59'.
    """

    profile = serializers.StringRelatedField(read_only=True)
    status = serializers.BooleanField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)
    executed_at = serializers.SerializerMethodField(read_only=True, allow_null=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_created_at(self, instance):
        return instance.created_at.strftime("%d/%m/%Y, %H:%M:%S")

    def get_executed_at(self, instance):
        if instance.executed_at is not None:
            return instance.executed_at.strftime("%d/%m/%Y, %H:%M:%S")
        return None

    def validate(self, data):
        # Validate a new order only if there are sufficient funds to execute it

        request_user = self.context.get('request').user
        user_wallet = get_object_or_404(Wallet, profile=request_user.profile)
        if data['type'] == 'B':
            required_dollar = data['price'] * data['quantity']
            if (user_wallet.available_dollar - required_dollar) < 0:
                raise serializers.ValidationError('insufficient balance')
        elif data['type'] == 'S':
            if (user_wallet.available_bitcoin - data['quantity']) < 0:
                raise serializers.ValidationError('insufficient balance')
        return data


class LatestOrdersSerializer(serializers.ModelSerializer):
    """
    ??
    """

    price = serializers.FloatField(read_only=True)
    quantity = serializers.FloatField(read_only=True)
    type = serializers.CharField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        exclude = ['profile', 'status', 'executed_at']

    def get_created_at(self, instance):
        return instance.created_at.strftime("%d/%m/%Y, %H:%M:%S")


class ProfileSerializer(serializers.ModelSerializer):
    """
    ??
    """

    profile = serializers.StringRelatedField(read_only=True)
    active_orders = serializers.SerializerMethodField(read_only=True)
    executed_orders = serializers.SerializerMethodField(read_only=True)
    dollar_balance = serializers.SerializerMethodField(read_only=True)
    bitcoin_balance = serializers.SerializerMethodField(read_only=True)
    bitcoin_profit = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        field = '__all__'

    def get_active_orders(self, instance):
        return instance.orders.filter(status=True).count()

    def get_executed_orders(self, instance):
        return instance.orders.filter(status=False).count()

    def get_dollar_balance(self, instance):
        return instance.wallet.available_dollar + instance.wallet.locked_dollar

    def get_bitcoin_balance(self, instance):
        return instance.wallet.available_bitcoin + instance.wallet.locked_bitcoin

    def get_bitcoin_profit(self, instance):
        return instance.wallet.available_bitcoin

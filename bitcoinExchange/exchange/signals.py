from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from exchange.models import Order, Profile, Wallet
from exchange.utils.trade import perform_trade


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a profile instance associated with the new user instance created.
    """

    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Profile)
def create_wallet(sender, instance, created, **kwargs):
    """
    Create a wallet instance associated with the new profile instance created.
    Save the initial bitcoin amount in the net balance in order to calculate profits.
    """

    if created:
        wallet = Wallet.objects.create(profile=instance)
        wallet.net_balance_bitcoin = wallet.available_bitcoin
        wallet.save()


@receiver(post_save, sender=Order)
def new_order(sender, instance, created, **kwargs):
    """
    Freeze the amount needed to fulfill the order when it is created.
    Perform the trade if there are compatible orders to match.
    """

    if created:
        instance_wallet = get_object_or_404(Wallet, profile=instance.profile)
        if instance.type == 'B':
            # Freeze the dollar amount if it is a buy order
            instance_wallet.freeze_amount(
                available_currency=instance_wallet.available_dollar,
                frozen_currency=instance_wallet.frozen_dollar,
                amount=instance.quantity * instance.price
            )

            # Check sell orders to match
            sell_orders = Order.objects.filter(type='S', status=True).exclude(profile=instance.profile)
            for sell_order in sell_orders:
                if instance.price >= sell_order.price and instance.quantity == sell_order.quantity:
                    sell_order_wallet = get_object_or_404(Wallet, profile=sell_order.profile)
                    perform_trade(instance, instance_wallet, sell_order, sell_order_wallet)
                    break

        elif instance.type == 'S':
            # Freeze the bitcoin amount if it is a sell order
            instance_wallet.freeze_amount(
                available_currency=instance_wallet.available_bitcoin,
                frozen_currency=instance_wallet.frozen_bitcoin,
                amount=instance.quantity
            )

            # Check buy orders to match
            buy_orders = Order.objects.filter(type='B', status=True).exclude(profile=instance.profile)
            for buy_order in buy_orders:
                if buy_order.price >= instance.price and buy_order.quantity == instance.quantity:
                    buy_order_wallet = get_object_or_404(Wallet, profile=buy_order.profile)
                    perform_trade(buy_order, buy_order_wallet, instance, instance_wallet)
                    break


@receiver(pre_delete, sender=Order)
def delete_order(sender, instance, **kwargs):
    """
    Unfreeze the amount needed to fulfill the order when it is canceled.
    """

    instance_wallet = get_object_or_404(Wallet, profile=instance.profile)
    if instance.type == 'B':
        # Unfreeze the dollar amount if it is a buy order
        instance_wallet.unfreeze_amount(
            available_currency=instance_wallet.available_dollar,
            frozen_currency=instance_wallet.frozen_dollar,
            amount=instance.price * instance.quantity
        )

    elif instance.type == 'S':
        # Unfreeze the bitcoin amount if it is a sell order
        instance_wallet.unfreeze_amount(
            available_currency=instance_wallet.available_bitcoin,
            frozen_currency=instance_wallet.frozen_bitcoin,
            amount=instance.quantity
        )

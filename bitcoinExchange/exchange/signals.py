from django.contrib.auth.models import User
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from exchange.models import Order, Profile, Wallet
from exchange.utils.trade import perform_trade


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a 'Profile' instance associated to the 'User' when a new 'User' instance is created.
    """

    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Profile)
def create_wallet(sender, instance, created, **kwargs):
    """
    Create a 'Wallet' instance associated to the 'Profile' when a new 'Profile' instance is created.
    """

    if created:
        Wallet.objects.create(profile=instance)


@receiver(post_save, sender=Order)
def new_order(sender, instance, created, **kwargs):
    """
    ??
    """

    if created:
        instance_wallet = get_object_or_404(Wallet, profile=instance.profile)
        if instance.type == 'B':
            instance_wallet.lock_dollar(instance.quantity * instance.price)
            sell_orders = Order.objects.filter(type='S', status=True).exclude(profile=instance.profile)
            for sell_order in sell_orders:
                if instance.price >= sell_order.price and instance.quantity == sell_order.quantity:
                    sell_order_wallet = get_object_or_404(Wallet, profile=sell_order.profile)
                    perform_trade(instance, instance_wallet, sell_order, sell_order_wallet)
                    break
        elif instance.type == 'S':
            instance_wallet.lock_bitcoin(instance.quantity)
            buy_orders = Order.objects.filter(type='B', status=True).exclude(profile=instance.profile)
            for buy_order in buy_orders:
                if buy_order.price >= instance.price and buy_order.quantity == instance.quantity:
                    buy_order_wallet = get_object_or_404(Wallet, profile=buy_order.profile)
                    perform_trade(buy_order, buy_order_wallet, instance, instance_wallet)
                    break


@receiver(pre_delete, sender=Order)
def delete_order(sender, instance, **kwargs):
    """
    ??
    """

    user_wallet = get_object_or_404(Wallet, profile=instance.profile)
    if instance.type == 'B':
        user_wallet.unlock_dollar(instance.price * instance.quantity)
    elif instance.type == 'S':
        user_wallet.unlock_bitcoin(instance.quantity)

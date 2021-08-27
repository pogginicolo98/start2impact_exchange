from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from exchange.models import Profile, Wallet


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

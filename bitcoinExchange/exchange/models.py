from django.contrib.auth.models import User
from djongo import models
from random import uniform


class Profile(models.Model):
    """
    User profile.
    Extension of the default 'User' model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['user']


class Order(models.Model):
    """
    Exchange order.
    Each user can create sales and purchase orders.

    fields
    - Type: False=sell, True=buy.
    - Status: Buy, Sell.
    - Created_at: Date format '31/12/2021, 23:59:59'.
    """

    # Order types
    CHOICES = (
        ('B', 'Buy'),
        ('S', 'Sell')
    )

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='orders')
    price = models.FloatField()
    quantity = models.FloatField()
    type = models.CharField(max_length=20, choices=CHOICES)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.created_at.strftime("%d/%m/%Y, %H:%M:%S")

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']


class Wallet(models.Model):
    """
    User wallet.
    Each user has only one wallet.
    """

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    dollars = models.FloatField(default=0)
    bitcoins = models.FloatField(default=uniform(1, 10))

    def __str__(self):
        return str(self.profile)

    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        ordering = ['profile']

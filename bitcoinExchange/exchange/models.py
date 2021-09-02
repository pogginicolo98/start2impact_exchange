from django.contrib.auth.models import User
from djongo import models
from random import uniform


class Profile(models.Model):
    """
    User profile.
    Extension of the default 'User' model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['user']

    def __str__(self):
        return self.user.username


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
    ORDER_TYPES = (
        ('B', 'Buy'),
        ('S', 'Sell')
    )

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='orders')
    price = models.FloatField()
    quantity = models.FloatField()
    type = models.CharField(max_length=20, choices=ORDER_TYPES)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.profile} - {self.type}'


class Wallet(models.Model):
    """
    User wallet.
    Each user has only one wallet.
    """

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    available_dollar = models.FloatField(default=0)
    locked_dollar = models.FloatField(default=0)
    available_bitcoin = models.FloatField(default=uniform(1, 10))
    locked_bitcoin = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        ordering = ['profile']

    def __str__(self):
        return str(self.profile)

    def lock_dollar(self, amount):
        self.available_dollar -= amount
        self.locked_dollar += amount
        self.save()

    def unlock_dollar(self, amount):
        self.available_dollar += amount
        self.locked_dollar -= amount
        self.save()

    def lock_bitcoin(self, amount):
        self.available_bitcoin -= amount
        self.locked_bitcoin += amount
        self.save()

    def unlock_bitcoin(self, amount):
        self.available_bitcoin += amount
        self.locked_bitcoin -= amount
        self.save()

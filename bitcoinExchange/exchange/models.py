from django.contrib.auth.models import User
from djongo import models
from random import uniform


class Profile(models.Model):
    """
    User profile.
    Extension of the default user model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['user']

    def __str__(self):
        return self.user.username


class Transaction(models.Model):
    """
    Transaction between 2 users.
    Each transaction consists of 2 compatible orders.

    :fields
    - executed_at: Datetime format '31/12/2021, 23:59:59'.
    """

    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-executed_at']

    def __str__(self):
        return self.executed_at.strftime("%d/%m/%Y, %H:%M:%S")


class Order(models.Model):
    """
    Exchange order.
    Each user can create multiple buy/sell orders.

    :fields
    - type: Buy/Sell.
    - status: False=executed, True=active.
    - created_at: Date format '31/12/2021, 23:59:59'.
    """

    # Order types
    ORDER_TYPES = (
        ('B', 'Buy'),
        ('S', 'Sell')
    )

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    price = models.FloatField()
    quantity = models.FloatField()
    type = models.CharField(max_length=20, choices=ORDER_TYPES)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='orders',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return self.created_at.strftime("%d/%m/%Y, %H:%M:%S")


class Wallet(models.Model):
    """
    Wallet associated with user instance.
    Each user has only one wallet.

    :fields
    - bitcoin_net_balance: Bitcoin net balance in order to calculate profits.
    """

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    bitcoin_net_balance = models.FloatField(blank=True, null=True)
    available_dollar = models.FloatField(default=0)
    frozen_dollar = models.FloatField(default=0)
    available_bitcoin = models.FloatField(default=uniform(1, 10))
    frozen_bitcoin = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        ordering = ['profile']

    def __str__(self):
        return str(self.profile)

    def freeze_amount(self, available_currency, frozen_currency, amount):
        """
        Freeze an amount of dollar/bitcoin.

        :argument
        - available_currency: Must be a wallet attribute (ex. available_dollar).
        - frozen_currency: Must be a wallet attribute (ex. frozen_dollar).
        """
        available_currency -= amount
        frozen_currency += amount
        self.save()

    def unfreeze_amount(self, available_currency, frozen_currency, amount):
        """
        Unfreeze an amount of dollar/bitcoin.

        :argument
        - available_currency: Must be a wallet attribute (ex. available_dollar).
        - frozen_currency: Must be a wallet attribute (ex. frozen_dollar).
        """

        available_currency += amount
        frozen_currency -= amount
        self.save()

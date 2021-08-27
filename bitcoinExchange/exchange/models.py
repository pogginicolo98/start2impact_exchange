from django.contrib.auth.models import User
from djongo import models
from random import uniform


class Profile(models.Model):
    """
    ???
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
    ???
    """

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='orders')
    datetime = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    quantity = models.FloatField()
    type = models.BooleanField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.datetime.strftime("%d/%m/%Y, %H:%M:%S")

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-datetime']


class Wallet(models.Model):
    """
    ???
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

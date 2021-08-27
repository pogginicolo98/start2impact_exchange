from django.contrib.auth.models import User
from djongo import models


class Profile(models.Model):
    """
    ???
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ips = models.Field(default=[])
    subprofiles = models.Field(default={})

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

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    quantity = models.FloatField()

    def __str__(self):
        return self.datetime.strftime("%d/%m/%Y, %H:%M:%S")

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-datetime']

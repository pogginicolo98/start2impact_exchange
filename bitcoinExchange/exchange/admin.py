from django.contrib import admin
from exchange.models import Order, Profile, Wallet

admin.site.register(Order)
admin.site.register(Profile)
admin.site.register(Wallet)

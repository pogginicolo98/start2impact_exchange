from django.contrib import admin
from exchange.models import Order, Profile, Transaction, Wallet

admin.site.register(Order)
admin.site.register(Profile)
admin.site.register(Transaction)
admin.site.register(Wallet)

from django.contrib import admin
from transactions.models import Transaction, WalletTransacton
# Register your models here.
admin.site.register(Transaction)
admin.site.register(WalletTransacton)
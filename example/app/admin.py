from django.contrib import admin

# Register your models here.

from .models import Account, Customer, Transaction

admin.site.register(Account)
admin.site.register(Customer)
admin.site.register(Transaction)

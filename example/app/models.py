from __future__ import unicode_literals

import random

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

from .signals import update_account


@python_2_unicode_compatible
class Customer(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField()

    def save(self, **kwargs):
        self.last_updated = timezone.now()
        super(Customer, self).save(**kwargs)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Account(models.Model):
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE)
    account_no = models.CharField(max_length=200)
    balance = models.DecimalField(max_digits=10, max_length=10,
                                  decimal_places=2)
    creation_date = models.DateTimeField(null=True)
    last_withdrawn = models.DateTimeField(null=True)
    last_deposited = models.DateTimeField(null=True)

    @property
    def transaction_count(self):
        return Transaction.objects.filter(account=self).count()

    def save(self, **kwargs):
        if not self.id:
            acc_no = ''.join(random.choice('0123456789ABCDEF')
                             for _ in range(5))
            self.account_no = acc_no
            self.creation_date = timezone.now()
        super(Account, self).save(**kwargs)

    def __str__(self):
        return self.account_no


@python_2_unicode_compatible
class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=200)
    transaction_date = models.DateTimeField()
    exchange = models.DecimalField(max_digits=9, max_length=9,
                                   decimal_places=2)
    is_fraudulent = models.BooleanField(default=False)
    is_reviewed = models.BooleanField(default=False)

    @property
    def is_deposit(self):
        return self.exchange > 0

    @property
    def deposit_or_withdrawal(self):
        if self.exchange > 0:
            return "deposit"
        return "withdrawal"

    def save(self, **kwargs):
        new_balance = self.account.balance + self.exchange
        if new_balance < 0:
            raise ValidationError("Transaction cannot be completed. Requested "
                                  "amount is greater than account balance.")
        self.transaction_date = timezone.now()
        rand_id = ''.join(random.choice('0123456789ABCDEF') for _ in range(10))
        self.transaction_id = rand_id
        super(Transaction, self).save(**kwargs)

    def __str__(self):
        return self.transaction_id

post_save.connect(update_account, sender=Transaction)

from __future__ import unicode_literals

import random

from django.utils import timezone


def update_account(sender, instance, **kwargs):
    account = instance.account
    account.balance += instance.exchange
    if instance.exchange > 0:
        account.last_deposited = timezone.now()
    else:
        account.last_withdrawn = timezone.now()
    account.save()


def _get_random_boolean(true_probability=0.5):
    val = random.random()
    if val < true_probability:
        return False
    return True


def populate_models(sender, **kwargs):
    from .models import Customer, Account, Transaction
    if Customer.objects.count() != 0:
        return

    random.seed(1729)

    print(u"Populating sample data for demo...")

    customer1 = Customer.objects.create(
        name=u'Honey Bunny',
        address=u'13763 Hawthorne Boulevard Hawthorne, CA 90250'
    )
    account1 = Account.objects.create(
        owner=customer1, balance=random.randrange(100, 10000000)
    )
    customer2 = Customer.objects.create(
        name=u'Jimmie',
        address=u'4145 Kraft Avenue Studio City, CA 91604'
    )
    account2 = Account.objects.create(
        owner=customer2, balance=random.randrange(100, 10000000)
    )
    customer3 = Customer.objects.create(
        name=u'Butch Coolidge',
        address=u'2934 Riverside Drive Los Angeles, CA 90039'
    )
    account3 = Account.objects.create(
        owner=customer3, balance=random.randrange(100, 10000000)
    )
    customer4 = Customer.objects.create(
        name=u'Marsellus Wallace',
        address=u'1541 Summitridge Drive Beverly Hills, CA 90210'
    )
    account4 = Account.objects.create(
        owner=customer4, balance=random.randrange(100, 10000000)
    )
    customer5 = Customer.objects.create(
        name=u'Mia Wallace',
        address=u'1541 Summitridge Drive Beverly Hills, CA 90210'
    )
    account5 = Account.objects.create(
        owner=customer5, balance=random.randrange(100, 10000000)
    )

    print("5 Customers instances created.")
    print("5 Account instances created.")

    accounts = [account1, account2, account3, account4, account5]
    for account in accounts:
        for _ in list(range(5)):
            Transaction.objects.create(
                account=account,
                exchange=random.randrange(100, 1000000) - 500000,
                # set about 20% of transactions to be fraudulent
                is_fraudulent=_get_random_boolean(0.8)
            )

    print("25 Transaction instances created.")
    print("Completed.")

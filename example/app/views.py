from __future__ import unicode_literals

import csv

from django.views.generic import TemplateView

from export_csv.views import ExportCSV

from .models import Customer, Account, Transaction


class IndexView(TemplateView):
    """View which renders index page."""
    template_name = 'app/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['customers'] = Customer.objects.all()
        context['accounts'] = Account.objects.all()
        context['transactions'] = Transaction.objects.all().order_by(
            'transaction_id'
        )
        return context


class CustomerCSV(ExportCSV):
    """View for creating and rendering CSV of all Customer model instances."""
    model = Customer


class AccountCSV(ExportCSV):
    """View for creating and rendering CSV of Account instances returned by
    custom queryset.
    """
    # use this filename for rendering CSV
    filename = 'rich_account_list.csv'

    def get_queryset(self):
        """Write to CSV only those Account instances whose balance is greater
        than 600000."""
        return Account.objects.filter(balance__gt=600000)

    def get_field_names(self):
        """Write to CSV only account_no and owner fields."""
        return ['account_no', 'owner']


class TransactionCSV(ExportCSV):
    model = Transaction
    field_names = ['account', 'transaction_id', 'transaction_date']
    filename = 'transactions_csv_filename.csv'

    def get_csv_writer_kwargs(self, **kwargs):
        return dict(quoting=csv.QUOTE_ALL, delimiter=b' ', quotechar=b'|')

    def clean_transaction_id(self, value):
        return str(value).lower()

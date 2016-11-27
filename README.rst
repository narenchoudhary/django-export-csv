django-export-csv
=================

.. image:: https://travis-ci.org/narenchoudhary/django-export-csv.svg?branch=master
    :target: https://travis-ci.org/narenchoudhary/django-export-csv
    :alt: CI status

.. image:: https://codecov.io/gh/narenchoudhary/django-export-csv/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/narenchoudhary/django-export-csv
    :alt: Coverage Status

.. image:: https://requires.io/github/narenchoudhary/django-export-csv/requirements.svg?branch=master
     :target: https://requires.io/github/narenchoudhary/django-export-csv/requirements/?branch=master
     :alt: Requirements Status

.. image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
    :target: https://opensource.org/licenses/BSD-3-Clause
    :alt: License Status

``django-export-csv`` is a reusable Django application for which provides generic views for downloading CSV files.


Installation
============

To get started using ``django-export-csv`` simply install it with

.. code-block:: python

    pip install git+https://github.com/narenchoudhary/django-export-csv#egg=django-export-csv


Usage
=====

Add ``'export_csv'`` to INSTALLED_APPS settings of the project.

.. code-block:: python

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        ...
        ...
        'export_csv',
    ]



Subclass ``ExportCSV`` in views.py file and provide model attribute.


.. code-block:: python

    from export_csv.views import ExportCSV

    from .models import Account

    class AccountCSV(ExportCSV):
        """View for creating and rendering CSV of all Account model instances."""
        model = Customer



In urls.py, add url pointing to the view class ``AccountCSV`` declared above.

.. code-block:: python

    from .views import AccountCSV

    urlpatterns = [
        (r'^account_csv/$', AccountCSV.as_view(), name='account-csv'),
    ]


That's it. It will render a CSV file containing all the fields of all the instances of ``Account`` model.

Customizing ExportCSV View
==========================

.. note::
    All examples follow from the models in the example project.

Use custom queryset
-------------------

By default, all instances of the ``model`` are included in (the queryset and)
the CSV.

To provide a custom queryset, override ``get_queryset`` method to return
custom queryset.

.. code-block:: python

    class AccountCSV(ExportCSV):
        model = Account

        def get_queryset(self):
            return Account.object.filter(is_active=True)


Only include certain fields of the model
----------------------------------------

It is possible that only some fields of the ``model`` are needed.

This can be achieved in two ways:

- provide ``field_names`` list

- override ``get_field_names`` method

.. code-block:: python

    class AccountCSV(ExportCSV):
        model = Account
        field_names = ['owner', 'account_no', 'balance']


.. code-block:: python

    class AccountCSV(ExportCSV):
        model = Account

        def get_field_names(self):
            return ['owner', 'account_no', 'balance']

Provide filename
----------------

By default, the CSV rendered will have filename *<model>_list.csv*. For
example, for ``Account`` model the filename will be *account_list.csv*.

Custom file name can be provided using two ways.

- provide ``filename`` attribute
- Override ``get_filename`` method.

.. code-block:: python

    class AccountCSV(ExportCSV):
        model = Account
        filename = 'active_account_list.csv'

        def get_queryset(self):
            return Account.object.filter(is_active=True)


.. code-block:: python

    class AccountCSV(ExportCSV):
        model = Account

        def get_queryset(self):
            return Account.object.filter(is_active=True)

        def get_filename(self):
            return 'active_account_list.csv'

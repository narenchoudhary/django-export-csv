django-export-csv
=================

``django-export-csv`` is a reusable Django application for which provides generic views for downloading CSV files.


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

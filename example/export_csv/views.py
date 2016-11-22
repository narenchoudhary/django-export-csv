from __future__ import unicode_literals

import csv

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.utils.encoding import force_str, force_text
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View


class ExportCSV(View):
    """
    Generic View class which handles exporting queryset to CSV file and
    rendering the response.

    Attributes:
        :model: optional name of a model. If provided, all objects of the
        model will for the queryset. If omitted, :get_queryset method must be
        overridden.

        :fields: an optional list of field names which are retrieved from
        queryset and written to CSV. If provided, only the named fields will be
        included in the CSV. If omitted all fields of the model will be used.
        Fields will be written in the CSV in the order of their occurrence in
        list.

        :filename: an optional string which forms name of csv returned in the
        response. If omitted, 'model_list.csv' will be used.

        :add_col_names: Boolean to determine whether to add header row in the
        CSV or not. Default value if False.

        :col_names: an optional list of strings which forms the header row of
        the CSV. If omitted, CSV will be created without any header row.

        :content_type: the content_type header of the response. Default value
        is 'text/csv' and should not be overridden.

        :csv_writer_dialect: dialect argument for csv.writer() method. Default
        value is 'excel'. It has been added just for sake for completeness.
    """

    http_method_names = ['options', 'head', 'get']
    model = None
    field_names = []
    filename = None
    add_col_names = False
    col_names = []
    _content_type = 'text/csv'
    csv_writer_dialect = 'excel'

    def get_queryset(self):
        """Returns the queryset for generating CSV.

        By default, it returns all instances of the Model class referred by
        model attribute. Override this method to supply custom queryset.
        """
        if self.model is not None:
            queryset = self.model.objects.all()
        else:
            raise ImproperlyConfigured(
                _("No model to get queryset from. Either provide a model or "
                    "override get_queryset method.")
            )
        return queryset

    def get_field_names(self):
        """Returns the fields names to be included in the CSV.

        By default, it returns the field_names attribute of the class. If
        fields attribute is `None`, it returns names of all the fields of the
        Model class referred by model attribute.
        """
        if self.field_names:
            return self.field_names
        if self.model is not None:
            model_fields = self.model._meta.fields
            fields = [f.name for f in model_fields]
            return fields
        else:
            raise ImproperlyConfigured(
                _("No model to get fields form. Either provide a model or "
                  "override get_fields method.")
            )

    def _get_field_verbose_names(self):
        if self.model is None:
            return None
        model_fields = self.model._meta.fields
        verbose_names = [f.verbose_name for f in model_fields]
        return verbose_names

    def get_col_names(self):
        """Returns column names"""
        if self.col_names:
            return self.col_names
        return None

    def get_filename(self):
        """Returns filename."""
        if self.filename is not None:
            return self.filename
        if self.model is not None:
            model_name = str(self.model.__name__).lower()
            self.filename = force_str(model_name + '_list.csv')
        else:
            raise ImproperlyConfigured(
                _("No model to generate filename. Either provide model or "
                  "filename or override get_filename method.")
            )
        return self.filename

    def get_csv_writer_dialect(self):
        return self.csv_writer_dialect

    def get_csv_writer_kwargs(self, **kwargs):
        """Returns the kwargs to be passed to csv.writer().

        Overridden this method to pass keyword arguments to csv.writer().
        Please keep in mind the string encoding differences between Python2
        and Python3 when dealing with multiple versions.

        Example:
        def get_csv_writer_kwargs(self, **kwargs):
            return dict(quoting=csv.QUOTE_ALL, delimiter=b' ', quotechar=b'|')
        """
        return kwargs

    def _create_csv(self):
        """Create CSV and render the response."""
        response = HttpResponse(content_type=self._content_type)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            self.get_filename())

        # TypeError is raised mostly because of unicode and byte string issues
        try:
            wr = csv.writer(
                response,
                dialect=self.get_csv_writer_dialect(),
                **self.get_csv_writer_kwargs()
            )
        except TypeError as e:
            raise e

        self.col_names = self.get_col_names()
        if self.add_col_names and self.col_names:
            wr.writerow(self.col_names)

        queryset = self.get_queryset()
        fields = self.get_field_names()
        if queryset is not None:
            for obj in queryset:
                row = []
                for field in iter(fields):
                    # If defined, get_field_<field_name> method will try to get
                    # value of the field. It can be any function. The purpose
                    # of this function to get raw data, not reshape it. Read
                    # docs for complete documentation and examples.
                    if hasattr(self, 'get_field_%s' % field):
                        val_func = getattr(self, 'get_field_%s' % field)
                        value = val_func(obj)
                    else:
                        value = getattr(obj, field)
                    # If defined, clean_<field_name> method will try transform
                    # (or reshape or modify) the value of field obtained
                    # previously. For Eg. changing string to uppercase before
                    # writing to CSV.
                    if hasattr(self, 'clean_%s' % field):
                        clean_func = getattr(self, 'clean_%s' % field)
                        value = clean_func(value)
                    else:
                        value = force_text(value)
                    row.append(value)
                wr.writerow(row)
        return response

    def get(self, request):
        """Default get method."""
        return self._create_csv()

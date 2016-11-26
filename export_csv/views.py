from __future__ import unicode_literals

import csv

from django.http import HttpResponse
from django.utils.encoding import force_str, force_text
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from .exceptions import NoModelFoundException


class ExportCSV(View):
    """Generic View class which handles exporting queryset to CSV file and
    rendering the response.
    """

    http_method_names = ['options', 'head', 'get']
    model = None
    """
    Name of a model. If provided, all objects of the
    model will for the queryset. If omitted, :func:`get_queryset` method must
    be overridden.
    """

    field_names = None
    """
    List of ``model`` field names written to CSV. If provided, only those
    fields will be included in the CSV. If omitted, values return by
    :func:`get_field_names` is used.

    .. note:: Fields will be written in the CSV in the order of their
        occurrence in list.
    """
    filename = None
    """
    Name used for CSV file generated. If omitted, filename returned by
    :func:`get_filename` will be used as default file name.
    """

    add_col_names = False
    """
    Set this to ``True`` to add column names (header) to the CSV file. Default
    value is ``False``.
    """

    col_names = None
    """
    Column names to be used for writing the header row in the CSV file. If
    provided, those column names will be written to header row. If omitted,
    values returned by :func:``get_col_names`` are used.
    """

    _content_type = 'text/csv'
    """
     The content_type header of the response returned by :func:`get`` method.
     Default value is 'text/csv' and should not be overridden.
    """

    _csv_writer_dialect = 'excel'
    """
    View class uses :func:`csv.writer` to generate CSV. This is the
    ``dialect`` argument for :func:`csv.writer` method.
    """

    def get_queryset(self):
        """Returns the queryset for generating CSV.

        By default, it returns all instances of the Model class referred by
        ``model`` attribute. Override this method to provide custom queryset.

        :raises: NoModelFoundException

        :returns: :class:`QuerySet`
        """
        if self.model is not None:
            queryset = self.model.objects.all()
        else:
            exception_msg = "No model to get queryset from. Either provide " \
                            "a model or override get_queryset method."
            raise NoModelFoundException(_(exception_msg))
        return queryset

    def get_field_names(self):
        """Returns the fields names to be included in the CSV.

        It returns the value of ``field_names`` attribute, if ``field_names``
        is not empty. Otherwise it returns names of all the fields of the
        Model class referred by ``model`` attribute.

        :raises: NoModelFoundException

        :returns: list
        """
        if self.field_names:
            return self.field_names
        if self.model is not None:
            self.field_names = [f.name for f in self.model._meta.fields if
                                not f.auto_created]
            return self.field_names
        else:
            exception_msg = "No model to get field names from. Either " \
                            "provide a model or override get_fields method."
            raise NoModelFoundException(_(exception_msg))

    def _get_field_verbose_names(self):
        """Returns verbose names of fields returned by :func:`get_field_names`.

        :returns: list
        """
        field_names = self.get_field_names()
        if self.model is not None:
            verbose_names = [f.verbose_name for f in self.model._meta.fields
                             if f.name in field_names]
            return verbose_names
        else:
            exception_msg = "No model to get verbose field names from."
            raise NoModelFoundException(_(exception_msg))

    def get_col_names(self):
        """Returns column names to be used for writing header row of the CSV.

        It returns ``col_names``, if ``col_names`` is not an empty list.
        Otherwise, it returns the verbose names of all the fields.

        :raises: TypeError

        :returns: list
        """
        if self.col_names:
            if isinstance(self.col_names, list):
                return self.col_names
            else:
                raise TypeError(_('col_names must be a list.'))
        return self._get_field_verbose_names()

    def get_filename(self):
        """Returns filename.

        It returns the filename to be used for rendering CSV. If explicit
        filename is provided, that filename is returned. If omitted,
        <model>_list.csv is returned.

        :raises: NoModelFoundException

        :returns: str
        """
        if self.filename is not None:
            return self.filename
        if self.model is not None:
            model_name = str(self.model.__name__).lower()
            self.filename = force_str(model_name + '_list.csv')
        else:
            exception_msg = "No model to generate filename. Either provide " \
                            "model or filename or override get_filename " \
                            "method."
            raise NoModelFoundException(_(exception_msg))
        return self.filename

    def get_csv_writer_dialect(self):
        """Returns the dialect to be used with :func:`csv.writer`.

        :returns: str
        """
        return self._csv_writer_dialect

    def get_csv_writer_kwargs(self, **kwargs):
        """Returns the kwargs to be passed to :func:`csv.writer`.

        :param kwargs: kwargs to be passed to :func:`csv.writer`
        :type kwargs: dict
        :returns: dict -- kwargs to be passed to :func:`csv.writer`
        """
        return kwargs

    def _create_csv(self):
        """Create CSV and render the response.

        :raises: TypeError

        :returns: :class:`HttpResponse`
        """
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
        except TypeError:
            raise TypeError()

        # add header column only if self.add_col_names is True
        if self.add_col_names:
            self.col_names = self.get_col_names()
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
        """
        Default get method.

        :param request: request
        :type request: HttpRequest
        :returns: HttpResponse
        """
        return self._create_csv()

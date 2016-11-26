import mock
from debug_toolbar.panels import request

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from export_csv.exceptions import NoModelFoundException
from export_csv.views import ExportCSV

from .models import Customer


class ExportCSVTests(TestCase):

    def setUp(self):
        pass

    def setup_view(self, view, request, model=None, field_names=None,
                   filename=None, add_col_names=False, col_names=None,
                   *args, **kwargs):
        """Mimic :func:`as_view` callable but returns view instance.

        ``args`` and ``kwargs`` are the same you would pass to ``reverse()``.
        """
        view.request = request
        view.model = model
        view.field_names = field_names
        view.filename = filename
        view.add_col_names = add_col_names
        view.col_names = col_names
        view.args = args
        view.kwargs = kwargs
        return view

    def test_get_queryset_pass(self):
        request = RequestFactory().get("")
        view = ExportCSV()
        view = self.setup_view(view, request, model=Customer)
        queryset = view.get_queryset()
        self.assertEquals(queryset.model, Customer)

    def test_get_queryset_exception(self):
        request = RequestFactory().get("")
        view = ExportCSV()
        view = self.setup_view(view, request)
        self.assertRaises(NoModelFoundException, view.get_queryset)

    def test_get_field_names_custom(self):
        request = RequestFactory().get("")
        view = ExportCSV()
        field_names = ['name', 'address', 'is_active']
        view = self.setup_view(view, request, field_names=field_names)
        returned_field_names = view.get_field_names()
        self.assertEquals(field_names, returned_field_names)

    def test_get_field_names_model(self):
        request = RequestFactory().get("")
        view = ExportCSV()
        view = self.setup_view(view, request, model=Customer)
        expected_field_names = ['name', 'address', 'is_active', 'last_updated']
        field_names = view.get_field_names()
        self.assertEquals(set(field_names), set(expected_field_names))

    def test_get_field_names_exception(self):
        request = RequestFactory().get("")
        view = ExportCSV()
        view = self.setup_view(view, request)
        self.assertRaises(NoModelFoundException, view.get_field_names)

    @mock.patch('export_csv.views.ExportCSV.get_field_names')
    def test_get_field_verbose_names_custom(self, mock_get_field_names):
        request = RequestFactory().get("")
        view = ExportCSV()
        field_names = ['name', 'address', 'is_active']
        expected_verbose_names = ['name', 'address', 'Is Active']
        view = self.setup_view(view, request, model=Customer,
                               field_names=field_names)
        mock_get_field_names.return_value = field_names
        result_verbose_names = view._get_field_verbose_names()
        self.assertEquals(expected_verbose_names, result_verbose_names)

    @mock.patch('export_csv.views.ExportCSV.get_field_names')
    def test_get_field_verbose_names_model(self, mock_get_field_names):
        request = RequestFactory().get("")
        view = ExportCSV()
        expected_verbose_names = ['name', 'address', 'Is Active',
                                  'last updated']
        view = self.setup_view(view, request, model=Customer)
        mock_get_field_names.return_value = ['name', 'address', 'is_active',
                                             'last_updated']
        result_verbose_names = view._get_field_verbose_names()
        self.assertEquals(set(expected_verbose_names),
                          set(result_verbose_names))

    def test_get_col_names_model(self):
        request = RequestFactory().get("")
        view = ExportCSV()
        expected_col_names = ['name', 'address', 'Is Active',
                                  'last updated']
        view = self.setup_view(view, request, model=Customer)
        result_col_names = view.get_col_names()
        self.assertEquals(set(expected_col_names), set(result_col_names))

    def test_get_col_names_custom(self):
        request = RequestFactory().get("")
        view = ExportCSV()
        expected_col_names = ['name', 'address', 'Is Active',
                              'last updated']
        view = self.setup_view(view, request, model=Customer,
                               col_names=expected_col_names)
        result_col_names = view.get_col_names()
        self.assertEquals(set(expected_col_names), set(result_col_names))

    def test_get_col_names_exception(self):
        request = RequestFactory().get("")
        view = ExportCSV()
        view = self.setup_view(view, request, col_names="hello world")
        self.assertRaises(TypeError, view.get_col_names)

    def test_get_filename_custom(self):
        request = RequestFactory().get("")
        view = ExportCSV()
        expected_filename = "custom_filename.csv"
        view = self.setup_view(view, request, filename=expected_filename)
        result_filename = view.get_filename()
        self.assertEquals(set(expected_filename), set(result_filename))

    def test_get_filename_model(self):
        request = RequestFactory().get("")
        view = ExportCSV()
        expected_filename = "customer_list.csv"
        view = self.setup_view(view, request, model=Customer)
        result_filename = view.get_filename()
        self.assertEquals(set(expected_filename), set(result_filename))

    def test_get_filename_exception(self):
        request = RequestFactory().get("")
        view = ExportCSV()
        view = self.setup_view(view, request)
        self.assertRaises(NoModelFoundException, view.get_filename)

    def test_create_csv(self):
        request = RequestFactory().get("")
        view = ExportCSV()
        view = self.setup_view(view, request, model=Customer)
        response = view._create_csv()
        self.assertEquals(200, response.status_code)
        self.assertEquals('text/csv', response['Content-Type'])

    @mock.patch('export_csv.views.ExportCSV._create_csv')
    def test_get(self, mock_create_csv):
        request = RequestFactory().get("")
        view = ExportCSV()
        view = self.setup_view(view, request, model=Customer)
        mock_create_csv.return_value= HttpResponse(status=200, content_type='text/csv')
        response = view.get(request=request)
        self.assertEquals(200, response.status_code)
        self.assertEquals('text/csv', response['Content-Type'])

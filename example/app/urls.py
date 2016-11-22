from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^account/csv/$', views.AccountCSV.as_view(), name='account-csv'),
    url(r'^customer/csv/$', views.CustomerCSV.as_view(), name='customer-csv'),
    url(r'^transaction/csv/$', views.TransactionCSV.as_view(),
        name='transaction-csv'),
]

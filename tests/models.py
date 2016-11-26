from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Customer(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    last_updated = models.DateTimeField()

    def save(self, **kwargs):
        self.last_updated = timezone.now()
        super(Customer, self).save(**kwargs)

    def __str__(self):
        return self.name

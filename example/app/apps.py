from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AppConfig(AppConfig):
    name = 'app'

    def ready(self):
        from .signals import populate_models
        post_migrate.connect(populate_models, sender=self)

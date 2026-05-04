"""
App configuration for sniffer_app.
"""
from django.apps import AppConfig


class SnifferAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sniffer_app'
    verbose_name = 'Контейнер сниффера 802.11'
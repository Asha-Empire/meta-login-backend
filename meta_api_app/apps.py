from django.apps import AppConfig


class MetaApiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meta_api_app'
    verbose_name = 'Meta Backend APIs'
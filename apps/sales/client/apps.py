from django.apps import AppConfig


class ClientConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    label = "client"
    name = "apps.sales.client"
    verbose_name = "Client"

from django.apps import AppConfig


class AddressConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    label = "address"
    name = "apps.address"
    verbose_name = "Address"

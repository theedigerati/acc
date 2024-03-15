from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DepartmentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    label = "department"
    name = "apps.department"
    verbose_name = _("Department")

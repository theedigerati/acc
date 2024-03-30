from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.conf import settings
from tenant_users.tenants.tasks import provision_tenant
from apps.accounting.factory import AccountingFactory
from django.db import connection

logging = get_task_logger(__name__)


@shared_task(bind=True, retry_backoff=3, retry_kwargs={"max_retries": 5})
def setup_org_tenancy(self, org_id):
    Organisation = apps.get_model("organisation", "Organisation")
    Tenant = apps.get_model("organisation", "Tenant")
    logging.info(connection.schema_name)
    logging.info(Organisation.objects.all())
    org_object = Organisation.objects.get(id=int(org_id))

    if self.retries > 0:
        logging.info(
            "[Task Retry] Attempt %d/%d",
            self.request.retries,
            self.retry_kwargs["max_retries"],
        )

    logging.info("[Started] Creating Tenant for %s ...", org_object.name)
    tenant_slug = org_object.get_tenant_slug()
    provision_tenant(
        tenant_name=self.name,
        tenant_slug=tenant_slug,
        user_email=settings.BASE_TENANT_OWNER_EMAIL,
        is_staff=True,
    )
    org_tenant = Tenant.objects.get(slug=tenant_slug)
    Organisation.objects.filter(id=int(org_id)).update(tenant=org_tenant)
    logging.info("[Started] Creating default Financial Accounts")
    accounting_factory = AccountingFactory(org_tenant.schema_name)
    accounting_factory.generate_default_accounts()
    logging.info("[Finished] Tenancy setup done!")

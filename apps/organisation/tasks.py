from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps

logging = get_task_logger(__name__)


@shared_task(bind=True, retry_backoff=3, retry_kwargs={"max_retries": 5})
def setup_org_tenancy(self, org_id, request_user_id):
    Organisation = apps.get_model("organisation", "Organisation")
    org_object = Organisation.objects.get(id=int(org_id))

    if self.request.retries > 0:
        logging.info(
            "[Task Retry] Attempt %d/%d",
            self.request.retries,
            self.retry_kwargs["max_retries"],
        )

    logging.info("[Started] Creating Tenant for %s ...", org_object.name)
    org_object.create_tenant(request_user_id)
    logging.info("[Started] Creating default Financial Accounts")
    org_object.setup_default_accounts()
    logging.info("[Finished] Tenancy setup done!")

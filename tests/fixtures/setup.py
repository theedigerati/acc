import pytest
import contextlib
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient
from django_tenants.utils import schema_context
from tenant_users.tenants.utils import create_public_tenant
from tenant_users.tenants.models import ExistsError
from tenant_users.tenants.tasks import provision_tenant
from apps.user.models import User
from apps.organisation.models import Tenant
from mixer.backend.django import mixer

CLIENT_DOMAIN_NAME = "test.com"
PUBLIC_EMAIL = settings.BASE_TENANT_OWNER_EMAIL
TEST_USER_EMAIL = "test@localhost"
DEFAULT_PASSWORD = "password"
TEST_TENANT_SLUG = "test"
TENANT_SUBFOLDER_PREFIX = getattr(settings, "TENANT_SUBFOLDER_PREFIX", None)


@pytest.fixture()
def client(test_user):
    api_client = CustomAPIClient(SERVER_NAME=f"{TEST_TENANT_SLUG}.{CLIENT_DOMAIN_NAME}")
    url = reverse("jwt-login")
    res = api_client.post(url, {"email": test_user.email, "password": DEFAULT_PASSWORD})
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + res.data["access"])
    return api_client


@pytest.fixture()
def test_user(create_tenant_user):
    with contextlib.suppress(ExistsError):
        user = create_tenant_user(TEST_USER_EMAIL)
        return user


@pytest.fixture()
def create_tenant_user(test_tenant):
    def _create_tenant_user(email):
        with schema_context("public"):
            user = User.objects.create_user(
                email=email,
                password=DEFAULT_PASSWORD,
            )
        test_tenant.add_user(user)
        return user

    return _create_tenant_user


@pytest.fixture()
def test_tenant(make_test_tenant):
    make_test_tenant()
    tenant = Tenant.objects.get(slug=TEST_TENANT_SLUG)
    if not hasattr(tenant, "organisation"):
        mixer.blend("organisation.Organisation", tenant=tenant)
    return tenant


@pytest.fixture()
def make_test_tenant():
    _make_public_tenant()

    def _make_test_tenant(slug=TEST_TENANT_SLUG):
        with contextlib.suppress(ExistsError):
            provision_tenant(
                tenant_name=slug, tenant_slug=slug, user_email=PUBLIC_EMAIL
            )

    return _make_test_tenant


@schema_context("public")
def _make_public_tenant():
    settings.TENANT_USERS_DOMAIN = CLIENT_DOMAIN_NAME
    settings.ALLOWED_HOSTS += [f".{CLIENT_DOMAIN_NAME}"]
    with contextlib.suppress(ExistsError):
        create_public_tenant(CLIENT_DOMAIN_NAME, PUBLIC_EMAIL)


class CustomAPIClient(APIClient):
    def __init__(self, subfolder_tenancy=False, **kwargs):
        self.subfolder_tenancy = subfolder_tenancy
        super().__init__(**kwargs)

    def request(self, **kwargs):
        if self.subfolder_tenancy:
            kwargs["PATH_INFO"] = (
                f"/{TENANT_SUBFOLDER_PREFIX}/{TEST_TENANT_SLUG}" + kwargs["PATH_INFO"]
            )
        return super().request(**kwargs)

import pytest
from mixer.backend.django import mixer
from apps.organisation.models import Tenant


@pytest.fixture()
def org_address_object():
    """
    Org Address object created with mixer.
    """
    return mixer.blend("organisation.OrgAddress")


@pytest.fixture()
def organisation_data(org_address_object):
    return {
        "name": "New Organisation",
        "branch": "Lagos",
        "description": "The New Organisation",
        "address": org_address_object.to_dict(),
    }


@pytest.fixture()
def organisation_object(make_test_tenant):
    """
    Organisation object created with mixer.
    """
    org_name = "org2"
    make_test_tenant(org_name)
    tenant = Tenant.objects.get(slug=org_name)
    return mixer.blend(
        "organisation.Organisation",
        name=org_name,
        tenant=tenant,
    )


@pytest.fixture()
def org_added_users(test_tenant):
    """
    Users added to organisation_object.
    """
    users = mixer.cycle(2).blend("user.User", tenants=[])
    for user in users:
        test_tenant.add_user(user)
    return users


@pytest.fixture()
def users_without_org():
    """
    Users that do not belong to any organisation.
    """
    return mixer.cycle(2).blend("user.User", tenants=[])


@pytest.fixture()
def org_users_data(org_added_users, users_without_org):
    """
    A collection users that belong to the organisation_object
    and users that do not belong to any organisation.
    """
    return {
        "users": [user.id for user in users_without_org]
        + [user.id for user in org_added_users]
    }

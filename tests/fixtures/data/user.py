import pytest
from mixer.backend.django import mixer


@pytest.fixture()
def user_data():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@localhost",
        "role": "employee",
    }


@pytest.fixture()
def user_data_partial():
    return {
        "last_name": "Dean",
        "email": "johndoe@localhost",
    }


@pytest.fixture()
def user_object_without_org():
    """
    User object that does not belong to test organisation,
    created with mixer.
    """
    return mixer.blend("user.User")


@pytest.fixture()
def user_object_with_org(test_tenant):
    """
    User object that belongs to test organisation(tenant),
    created with mixer.
    """
    user = mixer.blend("user.User", tenants=[])
    test_tenant.add_user(user)
    user.assign_default_permissions()
    return user

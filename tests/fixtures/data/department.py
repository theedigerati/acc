import pytest
from mixer.backend.django import mixer
from django_tenants.utils import tenant_context


@pytest.fixture()
def dept_object(test_tenant):
    """
    Department object created with mixer.
    """
    with tenant_context(test_tenant):
        return mixer.blend("department.Department", heads=[])


@pytest.fixture()
def dept_data(create_tenant_user, test_tenant, test_user, dept_object):
    """
    Sample department data.
    Permissions are the same with 'dept_object' permissions because
    mgt. user access is required to change a department's permissions.
    """
    user = create_tenant_user("dept.member2@localhost")
    with tenant_context(test_tenant):
        dept_object.user_set.add(user.tenant_perms)
    return {
        "name": "accounting",
        "description": "All organisation accountants",
        "permissions": [perm.id for perm in dept_object.permissions.all()],
        "heads": [user.id, test_user.id],
    }


@pytest.fixture()
def dept_data_partial():
    return {"name": "management", "description": "All management users"}

import pytest
from django.urls import reverse


@pytest.mark.django_db()
def test_create_list_account(client, test_user, account_data):
    url = reverse("account-list")
    # no permissions
    res = client.post(url, account_data, format="json")
    assert res.status_code == 403
    res = client.get(url)
    assert res.status_code == 403

    test_user.add_permissions("add_account", "view_account")
    res_create = client.post(url, account_data, format="json")
    assert res_create.status_code == 201
    print(res_create.data["sub_type"]["id"])
    assert res_create.data["sub_type"]["id"] == account_data["sub_type"]
    res = client.get(url)
    assert res.status_code == 200

    # balances
    url = reverse("account-balance")
    res = client.get(url)
    assert res.status_code == 200
    assert res_create.data["id"] in res.data


@pytest.mark.django_db()
def test_retrieve_update_delete_account(
    client,
    test_user,
    account_data,
    editable_account_object,
    non_editable_account_object,
):
    url = reverse("account-detail", kwargs={"pk": editable_account_object.pk})
    # no permissions
    res = client.get(url)
    assert res.status_code == 403
    res = client.put(url, data=account_data, format="json")
    assert res.status_code == 403
    res = client.delete(url)
    assert res.status_code == 403

    test_user.add_permissions("view_account", "change_account", "delete_account")
    # retrieve
    res = client.get(url)
    assert res.status_code == 200
    assert res.data["code"] == editable_account_object.code

    # sibling accounts
    url = reverse("account-siblings", kwargs={"pk": editable_account_object.pk})
    res = client.get(url)
    assert res.status_code == 200
    assert res.data["sub_types"]
    assert res.data["accounts"]
    # transactions
    url = reverse("account-transactions", kwargs={"pk": editable_account_object.pk})
    res = client.get(url)
    assert res.status_code == 200

    # update
    url = reverse("account-detail", kwargs={"pk": editable_account_object.pk})
    res = client.put(url, account_data, format="json")
    assert res.status_code == 200
    # delete
    res = client.delete(url)
    assert res.status_code == 204
    # update fail
    url = reverse("account-detail", kwargs={"pk": non_editable_account_object.pk})
    res = client.put(url, account_data, format="json")
    assert res.status_code == 400
    # delete fail
    res = client.delete(url)
    assert res.status_code == 400

import pytest
from rest_framework import status

from .utils import API_PREFIX

url_members = f"{API_PREFIX}/members/"
url_members_by_id = url_members + "{id}/"


@pytest.mark.usefixtures("test_members")
def test_get_members(user_client):
    response = user_client.get(url_members)
    assert response.status_code == status.HTTP_200_OK
    fields = ("id", "full_name", "department", "position")
    json_response = response.json()[0]
    errors = [field for field in fields if field not in json_response]
    assert not errors, f"Response must contain:\n" + "\n".join(errors)
    assert len(fields) == len(json_response)


@pytest.mark.usefixtures("test_members_with_profile", "test_member")
def test_filter_members(user_client):
    url = url_members + "?city=City1&position=Инженер"
    response = user_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert isinstance(json_response, list)
    assert len(json_response) == 1


@pytest.mark.usefixtures("test_members_with_profile", "test_member")
def test_search_and_filter_members(user_client):
    url = url_members + "?search=И&position=Position1"
    response = user_client.get(url)
    json_response = response.json()
    assert len(json_response) > 0, json_response
    print(json_response)

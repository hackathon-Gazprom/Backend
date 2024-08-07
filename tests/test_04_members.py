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

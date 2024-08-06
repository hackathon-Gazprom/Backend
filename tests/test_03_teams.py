import pytest
from rest_framework import status

from .utils import API_PREFIX

url_teams = f"{API_PREFIX}/teams/"
url_teams_by_id = url_teams + "{id}/"


@pytest.mark.usefixtures("test_team")
def test_get_teams(user_client):
    response = user_client.get(url_teams)
    assert response.status_code == status.HTTP_200_OK
    fields = ("id", "name", "description")
    json_response = response.json()[0]
    errors = [field for field in fields if field not in json_response]
    assert not errors, "response must contains:\n" + "\n".join(errors)
    assert len(json_response) == len(fields)


def test_team(user_client, test_team):
    response = user_client.get(url_teams_by_id.format(id=test_team.id))
    assert response.status_code == status.HTTP_200_OK
    fields = ("id", "name", "owner", "description", "employees")
    json_response = response.json()
    errors = [field for field in fields if field not in json_response]
    assert not errors, "response must contains:\n" + "\n".join(errors)
    assert len(json_response) == len(fields)
    assert isinstance(json_response["employees"], dict)

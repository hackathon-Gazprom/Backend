import pytest
from rest_framework import status

from .utils import API_PREFIX

url_teams = f"{API_PREFIX}/teams/"
url_teams_by_id = url_teams + "{id}/"
url_add_member_to_team = url_teams_by_id + "add_member/"


@pytest.mark.usefixtures("test_team")
def test_get_teams(user_client):
    response = user_client.get(url_teams)
    assert response.status_code == status.HTTP_200_OK
    fields = ("id", "name", "projects")
    json_response = response.json()[0]
    errors = [field for field in fields if field not in json_response]
    assert not errors, "response must contains:\n" + "\n".join(errors)
    assert len(json_response) == len(fields)
    assert isinstance(json_response["projects"], list)


def test_team(user_client, test_team):
    response = user_client.get(url_teams_by_id.format(id=test_team[0].id))
    assert response.status_code == status.HTTP_200_OK
    fields = ("id", "name", "owner", "description", "employees")
    json_response = response.json()
    errors = [field for field in fields if field not in json_response]
    assert not errors, "response must contains:\n" + "\n".join(errors)
    assert len(json_response) == len(fields)
    assert isinstance(json_response["employees"], dict)


@pytest.mark.parametrize(
    "current_client, expected_status",
    (
        (pytest.lazy_fixture("admin_client"), status.HTTP_200_OK),
        (pytest.lazy_fixture("user_client"), status.HTTP_403_FORBIDDEN),
    ),
)
def test_add_user_to_team(
    current_client, expected_status, user_with_profile, test_team
):
    data = {"user_id": user_with_profile.id, "parent_id": test_team[1].id}
    response = current_client.post(
        url_add_member_to_team.format(id=test_team[0].id), data=data
    )
    print(response.json())
    assert response.status_code == expected_status

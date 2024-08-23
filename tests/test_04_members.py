import pytest
from rest_framework import status

from .utils import API_PREFIX, MEMBER_FIELDS, check_fields

url_members = f"{API_PREFIX}/members/"
url_members_by_id = url_members + "{id}/"


@pytest.mark.usefixtures("test_members")
def test_get_members(user_client):
    response = user_client.get(url_members)
    assert response.status_code == status.HTTP_200_OK

    json_response = response.json()
    assert "results" in json_response

    check_fields(json_response["results"][0], MEMBER_FIELDS)


@pytest.mark.parametrize(
    "search, expected_fn",
    [
        ("?city=MyCity&position=Position1", lambda json: len(json) == 1),
        ("?search=И&position=Position1", lambda json: len(json) > 0),
        ("?department=Department 1", lambda json: len(json) > 0),
    ],
)
@pytest.mark.usefixtures("test_members_with_profile", "test_member")
def test_filter_members(user_client, search, expected_fn):
    url = url_members + search
    response = user_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()["results"]
    assert isinstance(json_response, list)
    assert expected_fn(json_response)

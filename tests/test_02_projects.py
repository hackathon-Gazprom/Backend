import pytest
from rest_framework import status

from api.v1.projects.constants import PROJECT_PAGE_SIZE

url_projects = "/api/v1/projects/"


@pytest.mark.usefixtures("create_projects")
def test_get_all_projects(admin_client):
    response = admin_client.get(url_projects)
    json_response = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(json_response["results"]) == PROJECT_PAGE_SIZE

    response = admin_client.get(json_response["next"])
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 8

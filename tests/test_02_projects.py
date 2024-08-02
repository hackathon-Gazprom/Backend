import pytest
from django.utils import timezone
from rest_framework import status

from api.v1.projects.constants import PROJECT_PAGE_SIZE
from apps.projects.models import Project

url_projects = "/api/v1/projects/"
url_project_by_id = "/api/v1/projects/{id}/"


@pytest.mark.usefixtures("create_projects")
def test_get_all_projects(admin_client):
    response = admin_client.get(url_projects)
    json_response = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(json_response["results"]) == PROJECT_PAGE_SIZE

    response = admin_client.get(json_response["next"])
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 8


def test_create_project(admin_client):
    data = {
        "name": "test_project",
        "description": "empty",
        "started": (timezone.now() + timezone.timedelta(days=1)).date(),
        "ended": (timezone.now() + timezone.timedelta(days=6)).date(),
    }
    project_count = Project.objects.count()
    response = admin_client.post(url_projects, data=data)
    assert response.status_code == status.HTTP_201_CREATED
    project_count += 1
    assert project_count == Project.objects.count()


def test_update_project(admin_client, test_project):
    new_data = {
        "ended": (timezone.now() + timezone.timedelta(days=5)).date(),
        "started": (timezone.now() + timezone.timedelta(days=4)).date(),
        "name": "New project name",
        "description": "New project description",
    }
    response = admin_client.patch(
        url_project_by_id.format(id=test_project.id), data=new_data
    )
    assert response.status_code == status.HTTP_200_OK

    json_response = response.json()
    assert json_response["name"] == new_data["name"]
    assert json_response["description"] == new_data["description"]
    assert json_response["started"] != new_data["started"]
    assert json_response["ended"] != new_data["ended"]


# TODO: change status
# TODO: change owner

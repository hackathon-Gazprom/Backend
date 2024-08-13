import pytest
from django.utils import timezone
from rest_framework import status

from apps.projects.models import Project
from .utils import API_PREFIX

url_projects = f"{API_PREFIX}/projects/"
url_project_by_id = url_projects + "{id}/"
url_project_change_status_by_id = url_project_by_id + "change_status/"
url_project_update_team_by_id = url_project_by_id + "update_team/"


@pytest.mark.usefixtures("create_projects")
def test_get_all_projects(admin_client):
    response = admin_client.get(url_projects)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert len(json_response) == 20


@pytest.mark.usefixtures("test_team")
def test_projects(admin_client):
    response = admin_client.get(url_projects)
    json_response = response.json()[0]
    teams = json_response["teams"]
    assert isinstance(teams, list)
    team = teams[0]
    fields = ("id", "name")
    errors = [f for f in fields if f not in team]
    assert not errors, "Response must contain fields:\n" + "\n".join(errors)
    assert len(team) == len(fields)


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


@pytest.mark.parametrize(
    ("current_client", "expected_status", "current_status"),
    (
        (
            pytest.lazy_fixture("admin_client"),
            status.HTTP_200_OK,
            Project.Status.STARTED,
        ),
        (
            pytest.lazy_fixture("user_client"),
            status.HTTP_403_FORBIDDEN,
            Project.Status.NOT_STARTED,
        ),
    ),
)
def test_change_status(
    current_client, test_project, expected_status, current_status
):
    data = {"status": Project.Status.STARTED.value}

    assert test_project.status == Project.Status.NOT_STARTED
    response = current_client.patch(
        url_project_change_status_by_id.format(id=test_project.id), data=data
    )
    test_project.refresh_from_db()
    assert response.status_code == expected_status
    assert test_project.status == current_status


@pytest.mark.parametrize(
    "current_client, expected_status",
    (
        (pytest.lazy_fixture("admin_client"), status.HTTP_200_OK),
        (pytest.lazy_fixture("user_client"), status.HTTP_403_FORBIDDEN),
    ),
)
@pytest.mark.usefixtures("test_teams")
def test_add_team_to_project(current_client, expected_status, test_project):
    data = {"team_id": 3}
    response = current_client.put(
        url_project_update_team_by_id.format(id=test_project.id), data=data
    )
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "current_client, expected_status, expected_change",
    (
        (pytest.lazy_fixture("admin_client"), status.HTTP_204_NO_CONTENT, 1),
        (pytest.lazy_fixture("user_client"), status.HTTP_403_FORBIDDEN, 0),
    ),
)
def test_delete_team_from_project(
    current_client,
    expected_status,
    expected_change,
    test_project,
    test_team,
):
    data = {"team_id": test_team.id}
    teams_count = test_project.teams.count()
    response = current_client.delete(
        url_project_update_team_by_id.format(id=test_project.id), data=data
    )
    assert response.status_code == expected_status
    assert test_project.teams.count() == teams_count - expected_change


def test_change_project_owner():
    pass  # TODO: check change owner
